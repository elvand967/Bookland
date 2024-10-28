# D:\Python\django\myLibrary\app\literon\models.py

from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator
from datetime import datetime
from django.template.defaultfilters import slugify
from django.utils.text import slugify
from .utilities import translit_re, generate_file_name  # моя функция транслитерации


class ModelCategories(models.Model):
    name = models.CharField(max_length=50, db_index=True, verbose_name="Жанр")
    slug = models.SlugField(max_length=50, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание"
    )

    def save(self, *args, **kwargs):
        # Генерация уникального слага
        self.slug = translit_re(self.name)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Проверяем, есть ли подкатегории и книги, связанные с категорией
        if self.subcategories.exists():  # subcategories - related_name для ForeignKey в ModelSubcategories
            for subcategory in self.subcategories.all():
                if subcategory.books.exists():  # books - related_name для ManyToManyField в ModelBooks
                    raise ValidationError(f"Нельзя удалить категорию '{self.name}', так как её подкатегория '{subcategory.name}' связана с книгами.")
            raise ValidationError(f"Нельзя удалить категорию '{self.name}', так как с ней связаны подкатегории.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("category", kwargs={"cat_slug": self.slug})

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ["id"]


class ModelSubcategories(models.Model):
    category = models.ForeignKey(
        'ModelCategories',  # Используем строковую ссылку на модель
        on_delete=models.CASCADE,
        related_name="subcategories",
        verbose_name="Жанр",
    )
    name = models.CharField(max_length=40, db_index=True, verbose_name="Поджанр")
    slug = models.SlugField(
        max_length=60, unique=True, db_index=True, verbose_name="URL"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание"
    )

    def save(self, *args, **kwargs):
        # Генерация уникального слага
        self.slug = f"{translit_re(self.name)}"
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Проверяем, есть ли книги, связанные с подкатегорией
        if self.books.exists():  # books - related_name для связи many-to-many с ModelBooks
            raise ValidationError("Нельзя удалить подкатегорию, так как с ней связаны книги.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse(
            "subcategory",
            kwargs={"cat_slug": self.category.slug, "subcat_slug": self.slug},
        )

    class Meta:
        verbose_name = "Поджанр"
        verbose_name_plural = "Поджанры"
        ordering = ["id"]


class Author(models.Model):
    surname_nick = models.CharField(max_length=60, verbose_name="Фамилия (nick)")
    name = models.CharField(max_length=60, blank=True, verbose_name="Имя")
    patronymic = models.CharField(max_length=60, blank=True, verbose_name="Отчество")
    slug = models.SlugField(max_length=60, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    class Meta:
        indexes = [models.Index(fields=['surname_nick', 'name'])]
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def clean(self):
        if not any([self.surname_nick, self.name]):
            raise ValidationError("Должно быть заполнено хотя бы одно поле: Фамилия (nick) или Имя.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate the instance

        # Генерация уникального слага
        self.slug = translit_re(f"{self.surname_nick} {self.name}".strip())

        super().save(*args, **kwargs)  # Save the instance

    def __str__(self):
        return f"{self.surname_nick} {self.name} {self.patronymic}".strip()

    def get_absolute_url(self):
        return reverse('author', kwargs={'slug': self.slug})


class Reader(models.Model):
    surname_nick = models.CharField(max_length=60, verbose_name="Фамилия (nick)")
    name = models.CharField(max_length=60, blank=True, verbose_name="Имя")
    patronymic = models.CharField(max_length=60, blank=True, verbose_name="Отчество")
    slug = models.SlugField(max_length=60, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание"
    )

    class Meta:
        indexes = [models.Index(fields=['surname_nick', 'name'])]
        verbose_name = "Чтец"
        verbose_name_plural = "Чтецы"

    def clean(self):
        if not any([self.surname_nick, self.name]):
            raise ValidationError("Должно быть заполнено хотя бы одно поле: Фамилия (nick) или Имя.")

    def save(self, *args, **kwargs):
        self.full_clean()

        # Генерация уникального слага
        self.slug = translit_re(f"{self.surname_nick} {self.name}".strip())

        super().save(*args, **kwargs)  # Save the instance

    def __str__(self):
        return f"{self.surname_nick} {self.name} {self.patronymic}".strip()

    def get_absolute_url(self):
        return reverse('reader', kwargs={'slug': self.slug})


class Cycle(models.Model):
    name = models.CharField(max_length=60, unique=True, verbose_name="Имя")
    slug = models.SlugField(max_length=60, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(blank=True, null=True, verbose_name="Описание цикла (серии)")
    # image = models.ImageField(upload_to='cycles/', blank=True, null=True, verbose_name="Обложка цикла")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = translit_re(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("cycle", kwargs={"cycle_slug": self.slug})

    class Meta:
        verbose_name = "Цикл (серия)"
        verbose_name_plural = "Циклы (серии)"


class ModelBooks(models.Model):
    WORK_TYPES = [
        ('short-story', 'Рассказ'),
        ('story', 'Повесть'),
        ('novel', 'Роман'),
        ('cycle', 'Цикл книг'),
        ('poem', 'Стихотворение'),
    ]
    title = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="Название аудиокниги"
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        db_index=True,
        verbose_name="URL",
        blank=True
    )
    book_subcategories = models.ManyToManyField(
        'ModelSubcategories',
        blank=True,
        verbose_name="Жанры"
    )
    work_type = models.CharField(max_length=15, choices=WORK_TYPES, default='novel', verbose_name="Тип произведения")
    cycle = models.ForeignKey(
        'Cycle',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Цикл"
    )
    cycle_number = models.CharField(max_length=10, blank=True, null=True, verbose_name='Номер в цикле')
    authors = models.ManyToManyField('Author', blank=True, verbose_name="Авторы")
    readers = models.ManyToManyField('Reader', blank=True, related_name='books', verbose_name="Чтецы")
    year = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1800), MaxValueValidator(datetime.now().year)],
        verbose_name="Год"
    )
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    duration = models.DurationField(blank=True, null=True, verbose_name="Продолжительность")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    is_published = models.BooleanField(default=True, verbose_name="Публикация")
    total_torrent_files = models.PositiveIntegerField(default=0, editable=False, verbose_name="Торрентов")
    total_audio_files = models.PositiveIntegerField(default=0, editable=False, verbose_name="Аудиофайлов")
    total_images = models.PositiveIntegerField(default=0, editable=False, verbose_name="Изображений")
    total_files = models.PositiveIntegerField(default=0, editable=False, verbose_name="Файлов")

    class Meta:
        verbose_name = "Аудиокнига"
        verbose_name_plural = "Аудиокниги"
        ordering = ["-year", "title"]

    def update_counters(self):
        self.total_torrent_files = self.torrent_files.count()  # Используем related_name
        self.total_audio_files = self.audio_files.count()  # Используем related_name
        self.total_images = self.book_images_set.count()  # Используем related_name
        self.total_files = self.additional_files_set.count()  # Используем related_name

    def __str__(self):
        authors_str = ", ".join(author.surname_nick for author in self.authors.all())
        return f"{self.title} | {authors_str}"

    def get_absolute_url(self):
        return reverse("audiobook", kwargs={"slug": self.slug})

    '''Что делает метод save:
- Проверяет и устанавливает слаг, если он не задан.
- Обнуляет поля cycle и cycle_number, если work_type не является циклом.
- Вызывает update_counters для обновления количества файлов.
- Валидирует данные с помощью full_clean().
- Сохраняет объект.'''
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while ModelBooks.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug

        if self.work_type != 'cycle':
            self.cycle = None
            self.cycle_number = None

        self.full_clean()
        super().save(*args, **kwargs)

        self.update_counters()
        super().save(update_fields=['total_torrent_files', 'total_audio_files', 'total_images', 'total_files'])

    def get_average_rating(self):
        pass

    def formatted_duration(self):
        if not self.duration:
            return None
        total_seconds = int(self.duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'{hours:02}:{minutes:02}:{seconds:02}'


# Модель для торрент-файлов
class TorrentFile(models.Model):
    book = models.ForeignKey(ModelBooks, on_delete=models.CASCADE, related_name='torrent_files')
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='torrent_files')
    file = models.FileField(
        upload_to='uploads/torrents/',
        validators=[FileExtensionValidator(allowed_extensions=['torrent'])],
        verbose_name="Торрент-файл"
    )

    class Meta:
        verbose_name = "Торрент-файл"
        verbose_name_plural = "Files-Torrent"

    def save(self, *args, **kwargs):
        self.file.name = generate_file_name(self, self.file.name, 'torrent')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Торрент для {self.book.title} чтец {self.reader.name}"


# Модель для хранения изображений книг
class BookImage(models.Model):
    book = models.ForeignKey(
        ModelBooks,
        on_delete=models.CASCADE,
        related_name='book_images_set',
        verbose_name="Книга"
    )
    image = models.ImageField(
        upload_to='uploads/book_images/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        verbose_name="Изображение"
    )

    class Meta:
        verbose_name = "Изображение книги"
        verbose_name_plural = "Files-Picture"

    def save(self, *args, **kwargs):
        if not self.image.name.startswith(self.book.slug):
            self.image.name = generate_file_name(self.book, self.image.name, 'image')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Изображение для {self.book.title}"


# Модель для хранения дополнительных файлов (например, текстовые файлы, архивы)
class AdditionalFile(models.Model):
    book = models.ForeignKey("ModelBooks", on_delete=models.CASCADE,
                             related_name='additional_files_set',
                             verbose_name="Аудиокнига")
    file = models.FileField(
        upload_to='uploads/extra_files/',
        validators=[FileExtensionValidator(allowed_extensions=['txt', 'fb2', 'pdf', 'zip', '7z', 'rar', 'zip'])],
        verbose_name="Дополнительный файл"
    )
    file_type = models.CharField(max_length=50, verbose_name="Тип файла", blank=True, null=True)

    class Meta:
        verbose_name = "Файлы"
        verbose_name_plural = "Files"

    def save(self, *args, **kwargs):
        if not self.file.name.startswith(self.book.slug):
            self.file.name = generate_file_name(self.book, self.file.name, 'additional')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Файл {self.file.name} для {self.book.title}"


# Модель для аудиофайлов
class AudioFile(models.Model):
    book = models.ForeignKey("ModelBooks", on_delete=models.CASCADE, related_name='audio_files',
                             verbose_name="Аудиокнига")
    file = models.FileField(
        upload_to='uploads/audio_files/',
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'm4b', 'aac', 'wav'])],
        verbose_name="Аудиофайл"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="№ файла")
    duration = models.DurationField(blank=True, null=True, verbose_name="Длительность")

    class Meta:
        verbose_name = "Аудиофайл"
        verbose_name_plural = "Files-Audio"
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.order == 0:  # Если у файла ещё нет номера
            max_order = self.book.audio_files.aggregate(models.Max('order'))['order__max'] or 0
            self.order = max_order + 1

        self.file.name = generate_file_name(self.book, self.file.name, 'audio')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.book.title} - часть {self.order}'


class SocialMediaPlatform(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Платформа")

    class Meta:
        ordering = ['name']  # Сортировка по умолчанию по названию платформы

    def __str__(self):
        return self.name

class SocialMediaLink(models.Model):
    book = models.ForeignKey(
        'ModelBooks',
        on_delete=models.CASCADE,
        related_name="social_media_links",
        verbose_name="Книга"
    )
    platform = models.ForeignKey(
        'SocialMediaPlatform',
        on_delete=models.CASCADE,
        verbose_name="Платформа"
    )
    url = models.URLField(verbose_name="Ссылка на пост/контент")
    description = models.TextField(blank=True, verbose_name="Описание поста (анонс, хештеги и т.д.)")
    post_date = models.DateField(null=True, blank=True, verbose_name="Дата публикации")
    video_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на видео (если есть)")

    def __str__(self):
        return f"{self.book.title} на {self.platform}"


class BookRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    book = models.ForeignKey(ModelBooks, on_delete=models.CASCADE, related_name='ratings')

    # Критерии голосования
    overall_score = models.PositiveSmallIntegerField(verbose_name="Общая оценка", default=0)  # Общая оценка, от 1 до 5
    narration_score = models.PositiveSmallIntegerField(verbose_name="Озвучка", default=0)  # Оценка озвучки, от 1 до 5
    quality_score = models.PositiveSmallIntegerField(verbose_name="Качество записи", default=0)  # Оценка качества звука
    plot_score = models.PositiveSmallIntegerField(verbose_name="Сюжет и содержание", default=0)  # Оценка сюжета
    length_feedback = models.CharField(
        max_length=100,
        choices=[('too_short', 'Слишком короткая'), ('perfect', 'Подходит по длине'), ('too_long', 'Слишком длинная')],
        verbose_name="Продолжительность", default='perfect'
    )
    would_recommend = models.BooleanField(verbose_name="Рекомендуете?", default=False)  # "Да/Нет"

    # Автоматическое добавление времени оценки
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Пользователь может оценивать каждую книгу только один раз
        unique_together = ['user', 'book']

    def __str__(self):
        return f"Оценка книги {self.book.title} от {self.user.username}"