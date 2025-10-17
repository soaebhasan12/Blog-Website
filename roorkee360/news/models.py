# models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from PIL import Image
import os

class Category(models.Model):
    """News categories like Historical, Trending, Local Events, etc."""
    CATEGORY_CHOICES = [
        ('historical', 'Historical'),
        ('trending', 'Trending'),
        ('local_events', 'Local Events'),
        ('education', 'Education'),
        ('business', 'Business'),
        ('sports', 'Sports'),
        ('culture', 'Culture'),
        ('government', 'Government'),
        ('weather', 'Weather'),
        ('announcements', 'Announcements'),
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'display_name']
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.display_name

class Tag(models.Model):
    """Tags for better content organization"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class NewsArticle(models.Model):
    """Main news article model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    subtitle = models.CharField(max_length=300, blank=True, help_text="Brief subtitle or summary")
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True, help_text="Short description for previews")
    
    # Categorization
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    
    # Media
    featured_image = models.ImageField(upload_to='news_images/%Y/%m/', blank=True, null=True)
    featured_image_alt = models.CharField(max_length=200, blank=True)
    featured_image_caption = models.CharField(max_length=300, blank=True)
    
    # Author and status
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="SEO keywords (comma separated)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement
    views_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, help_text="Show in featured section")
    is_breaking = models.BooleanField(default=False, help_text="Breaking news badge")
    
    # Location specific (for Roorkee)
    location = models.CharField(max_length=100, blank=True, help_text="Specific area in Roorkee")
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'published_at']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('news:article_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
        
        # Resize image if too large
        if self.featured_image:
            self.resize_image()
    
    def resize_image(self):
        """Resize featured image to optimize loading"""
        if self.featured_image:
            img_path = self.featured_image.path
            if os.path.exists(img_path):
                with Image.open(img_path) as img:
                    if img.width > 1200 or img.height > 800:
                        img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
                        img.save(img_path, optimize=True, quality=85)

class ArticleImage(models.Model):
    """Additional images for articles"""
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='article_images/%Y/%m/')
    caption = models.CharField(max_length=300, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.article.title}"

class Comment(models.Model):
    """User comments on articles"""
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField(max_length=1000)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.name} on {self.article.title}"

class NewsletterSubscriber(models.Model):
    """Newsletter subscribers"""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

# Future model for store promotions
class StorePromotion(models.Model):
    """For future store promotions feature"""
    store_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='promotions/%Y/%m/', blank=True)
    discount_percentage = models.PositiveIntegerField(null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    contact_info = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.store_name} - {self.title}"