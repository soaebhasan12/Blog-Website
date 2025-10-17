from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import NewsArticle, Category, Tag

def home_view(request):
    """Homepage with featured articles and latest news"""
    featured_articles = NewsArticle.objects.filter(
        status='published', is_featured=True
    )[:3]
    
    breaking_news = NewsArticle.objects.filter(
        status='published', is_breaking=True
    ).first()
    
    latest_articles = NewsArticle.objects.filter(
        status='published'
    ).exclude(is_featured=True)[:6]
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'featured_articles': featured_articles,
        'breaking_news': breaking_news,
        'latest_articles': latest_articles,
        'categories': categories,
    }
    return render(request, 'news/home.html', context)

def article_detail_view(request, slug):
    """Individual article view"""
    article = get_object_or_404(
        NewsArticle.objects.select_related('category', 'author').prefetch_related('tags'),
        slug=slug,
        status='published'
    )
    
    # Increment view count
    article.views_count += 1
    article.save(update_fields=['views_count'])
    
    # Related articles
    related_articles = NewsArticle.objects.filter(
        category=article.category,
        status='published'
    ).exclude(id=article.id)[:3]
    
    # Comments
    comments = article.comments.filter(is_approved=True)
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'comments': comments,
    }
    return render(request, 'news/article_detail.html', context)

def category_view(request, category_name):
    """Articles by category"""
    category = get_object_or_404(Category, name=category_name, is_active=True)
    
    articles_list = NewsArticle.objects.filter(
        category=category,
        status='published'
    )
    
    paginator = Paginator(articles_list, 12)
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'articles': articles,
    }
    return render(request, 'news/category.html', context)


def search_view(request):
    """Enhanced search functionality"""
    query = request.GET.get('q', '').strip()
    articles = []
    suggestions = []
    
    if query:
        # Search in title, content, excerpt, and subtitle
        articles_list = NewsArticle.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(subtitle__icontains=query),
            status='published'
        ).select_related('category', 'author').order_by('-published_at', '-created_at')
        
        # Get search suggestions for empty results
        if not articles_list.exists():
            suggestions = NewsArticle.objects.filter(
                status='published'
            ).values_list('title', flat=True)[:5]
        
        paginator = Paginator(articles_list, 10)
        page_number = request.GET.get('page')
        
        try:
            articles = paginator.page(page_number)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'query': query,
        'suggestions': suggestions,
    }
    return render(request, 'news/search.html', context)