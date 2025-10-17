# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Tag, NewsArticle, ArticleImage, Comment, NewsletterSubscriber

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'is_active', 'order', 'article_count']
    list_filter = ['is_active']
    search_fields = ['display_name', 'description']
    ordering = ['order', 'display_name']
    
    def article_count(self, obj):
        return obj.articles.filter(status='published').count()
    article_count.short_description = 'Published Articles'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'article_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'

class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 0
    fields = ['image', 'caption', 'order']

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'status', 'priority', 'is_featured', 
                   'views_count', 'published_at', 'created_at']
    list_filter = ['status', 'category', 'is_featured', 'is_breaking', 'priority', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    inlines = [ArticleImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'subtitle', 'content', 'excerpt')
        }),
        ('Categorization', {
            'fields': ('category', 'tags', 'location')
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_alt', 'featured_image_caption')
        }),
        ('Publication', {
            'fields': ('author', 'status', 'priority', 'is_featured', 'is_breaking')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ['collapse']
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'author')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'article', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['name', 'email', 'content', 'article__title']
    actions = ['approve_comments', 'reject_comments']
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments approved successfully.')
    approve_comments.short_description = "Approve selected comments"
    
    def reject_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments rejected.')
    reject_comments.short_description = "Reject selected comments"

    
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
