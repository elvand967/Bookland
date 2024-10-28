# D:\Python\myProject\Bookland\apps\bookland\admin.py


from django.contrib.admin.sites import site
from django.contrib import admin
from django.core.checks import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import *


class SubCategoriesInline(admin.TabularInline):
    """Отображение поджанров на странице жанров"""

    model = ModelSubcategories
    prepopulated_fields = {"slug": ("name",)}  # Заполняем слаг по поджанру
    extra = 1  # Количество пустых дополнительных поджанров для добавления


@admin.register(ModelCategories)
class ModelCategoriesAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)  # сортируем по имени категории
    # inlines = [SubCategoriesInline, ]  # Подключаем inline поджанров


@admin.register(ModelSubcategories)
class ModelSubcategoriesAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "slug", "description")
    list_display_links = ("name", "slug")  # поля-ссылки на экземпляр модели
    prepopulated_fields = {"slug": ("name",)}
    # search_fields = ('name', 'category__name')
    ordering = ("category", "name")  # порядок сортировки
    list_filter = ("category",)


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description")
    search_fields = ["name"]  # Поля, по которым будет производиться поиск
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)  # Сортируем по названию цикла

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        if "autocomplete" in request.GET:
            queryset = queryset.filter(name__icontains=search_term)
        return queryset, use_distinct


# @admin.register(TorrentFile)
# class TorrentFileAdmin(admin.ModelAdmin):
#     form = TorrentFileForm


class TorrentFileInline(admin.TabularInline):
    model = TorrentFile
    # form = TorrentFileForm
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)

        class WrapperFormSet(FormSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for form in self.forms:
                    form.fields["reader"].queryset = (
                        obj.readers.all() if obj else Reader.objects.none()
                    )

        return WrapperFormSet


@admin.register(BookImage)
class BookImageAdmin(admin.ModelAdmin):
    list_display = ("book_title", "image_preview", "image_filename")
    list_filter = ("book",)
    search_fields = ("book__title",)
    raw_id_fields = ("book",)

    def book_title(self, obj):
        return obj.book.title

    book_title.short_description = "Книга"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "Нет изображения"

    image_preview.short_description = "Предпросмотр"

    def image_filename(self, obj):
        return obj.image.name.split("/")[-1]

    image_filename.short_description = "Имя файла"

    fieldsets = ((None, {"fields": ("book", "image")}),)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # если это существующий объект
            return ("book",)
        return ()


class BookImageInline(admin.TabularInline):
    """Отображение дополнительных файлов картинок на странице книги"""

    model = BookImage
    extra = 1  # Количество пустых дополнительных файлов для добавления
    image = ("image",)  # Поля для отображения


@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = ("book", "order", "duration", "file")
    list_filter = ("book",)
    search_fields = ("book__title",)
    ordering = ("book", "order")

    fieldsets = ((None, {"fields": ("book", "file", "order", "duration")}),)

    readonly_fields = ("duration",)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # если это существующий объект
            return self.readonly_fields + ("book",)
        return self.readonly_fields


class AudioFileInline(admin.TabularInline):
    """Отображение аудиофайлов на странице книги"""

    model = AudioFile
    extra = 1  # Количество пустых аудиофайлов для добавления
    # fields = ('file', 'order', 'duration')  # Поля для отображения
    # readonly_fields = ('duration',)  # Поле только для чтения (длительность)


@admin.register(AdditionalFile)
class AdditionalFileAdmin(admin.ModelAdmin):
    list_display = ("book_title", "file_name", "file_type", "file_size", "file_link")
    list_filter = ("book", "file_type")
    search_fields = ("book__title", "file__name", "file_type")
    raw_id_fields = ("book",)

    def book_title(self, obj):
        return obj.book.title

    book_title.short_description = "Книга"

    def file_name(self, obj):
        return obj.file.name.split("/")[-1]

    file_name.short_description = "Имя файла"

    def file_size(self, obj):
        try:
            return f"{obj.file.size / 1024 / 1024:.2f} MB"
        except (ObjectDoesNotExist, FileNotFoundError):
            return "Файл не найден"

    file_size.short_description = "Размер файла"

    def file_link(self, obj):
        try:
            return format_html('<a href="{}" target="_blank">Скачать</a>', obj.file.url)
        except (ObjectDoesNotExist, FileNotFoundError):
            return "Файл не найден"

    file_link.short_description = "Ссылка"

    def file_link(self, obj):
        return format_html('<a href="{}" target="_blank">Скачать</a>', obj.file.url)

    file_link.short_description = "Ссылка"

    fieldsets = ((None, {"fields": ("book", "file", "file_type")}),)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # если это существующий объект
            return ("book",)
        return ()

    def save_model(self, request, obj, form, change):
        if not obj.file_type:
            file_extension = obj.file.name.split(".")[-1].lower()
            obj.file_type = file_extension

        # Проверяем существование файла перед сохранением
        if not default_storage.exists(obj.file.name):
            self.message_user(
                request,
                f"Внимание: файл {obj.file.name} не найден в хранилище.",
                level=messages.WARNING,
            )

        super().save_model(request, obj, form, change)


class AdditionalFileInline(admin.TabularInline):
    """Отображение дополнительных файлов на странице книги"""

    model = AdditionalFile
    extra = 1  # Количество пустых дополнительных файлов для добавления
    fields = ("file",)  # Поля для отображения


# Инлайн для отображения ссылок на социальные сети внутри админки книги
class SocialMediaLinkInline(admin.StackedInline):
    model = SocialMediaLink
    extra = 1  # Одна пустая строка для новой ссылки
    fields = ("platform", "url", "video_url", "description", "post_date")
    show_change_link = False  # Убрана ссылка на редактирование отдельно


# Админ-панель для модели платформ
@admin.register(SocialMediaPlatform)
class SocialMediaPlatformAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(ModelBooks)
class ModelBooksAdmin(admin.ModelAdmin):
    # form = ModelBooksForm  # Используем кастомную форму с автозаполнением поджанров
    list_display = (
        "title",
        "cycle",
        "cycle_number",
        "total_torrent_files",
        "total_audio_files",
        "total_images",
        "total_files",
        "is_published",
    )
    list_display_links = ("title",)  # Поля-ссылки на экземпляр модели
    list_editable = ("is_published",)  # Редактируемость полей в списке
    search_fields = (
        "title",
        "cycle",
    )  # Поля для поиска
    list_filter = ("is_published",)  # Фильтры для админки
    prepopulated_fields = {"slug": ("title",)}  # Автозаполнение поля slug
    filter_horizontal = (
        "book_subcategories",
        "authors",
        "readers",
    )
    ordering = (
        "cycle",
        "cycle_number",
        "title",
    )  # Сортируем по названию цикла, номеру в цикле названию книги
    """ Поля, которые можно редактировать в админке """
    fields = (
        "title",
        "slug",
        "book_subcategories",
        "authors",
        "readers",
        "description",
        "work_type",
        "cycle",
        "cycle_number",
        "is_published",
    )

    # Подключаем inlines для файлов и социальных сетей
    inlines = [
        TorrentFileInline,
        BookImageInline,
        AudioFileInline,
        AdditionalFileInline,
        SocialMediaLinkInline,
    ]

    # def get_inline_instances(self, request, obj=None):
    #     inline_instances = super().get_inline_instances(request, obj)
    #     for inline in inline_instances:
    #         if isinstance(inline, TorrentFileInline):
    #             inline.form.base_fields['book'].initial = obj
    #     return inline_instances


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("surname_nick", "name", "patronymic", "slug")
    prepopulated_fields = {"slug": ("surname_nick",)}  # Заполняем слаг по фамилии
    search_fields = ("surname_nick",)  # Поля для поиска
    ordering = ("surname_nick",)  # Сортируем по фамилии (нику) автора

    def save_model(self, request, obj, form, change):
        obj.full_clean()  # Валидация перед сохранением
        super().save_model(request, obj, form, change)  # Сохраняем объект


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ("surname_nick", "name", "patronymic", "slug")
    prepopulated_fields = {"slug": ("surname_nick",)}  # Заполняем слаг по фамилии
    search_fields = ("surname_nick",)  # Поля для поиска
    ordering = ("surname_nick",)  # Сортируем по фамилии (нику) чтеца

    def save_model(self, request, obj, form, change):
        obj.full_clean()  # Валидация перед сохранением
        super().save_model(request, obj, form, change)  # Сохраняем объект
