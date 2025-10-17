from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
import logging
from .models import NewsArticle, Category, Tag, Comment
from .forms import CommentForm


# Logger for debugging
logger = logging.getLogger(__name__)


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


@csrf_protect
def article_detail_view(request, slug):
    """Individual article view with comment functionality"""
    
    # Get article with related data
    article = get_object_or_404(
        NewsArticle.objects.select_related('category', 'author').prefetch_related('tags'),
        slug=slug,
        status='published'
    )
    
    # Increment view count (session-based to prevent abuse)
    session_key = f'viewed_article_{article.id}'
    if not request.session.get(session_key, False):
        article.views_count += 1
        article.save(update_fields=['views_count'])
        request.session[session_key] = True
        request.session.set_expiry(1800)  # 30 minutes
    
    # Initialize comment form
    comment_form = CommentForm()
    
    # Handle comment submission (POST request)
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        
        if comment_form.is_valid():
            try:
                # Create comment instance without saving to DB yet
                new_comment = comment_form.save(commit=False)
                new_comment.article = article
                
                # Auto-approve or require moderation
                # Set to False if you want manual approval in admin
                new_comment.is_approved = True
                
                # Save to database
                new_comment.save()
                
                # Success message
                messages.success(
                    request, 
                    '🎉 Thank you for your comment! It has been posted successfully.'
                )
                
                # Log the comment
                logger.info(f'New comment by {new_comment.name} on: {article.title}')
                
                # Redirect to avoid duplicate submission on refresh
                return redirect(f"{article.get_absolute_url()}#comments")
                
            except Exception as e:
                logger.error(f'Error saving comment: {str(e)}')
                messages.error(
                    request,
                    '❌ There was an error posting your comment. Please try again.'
                )
        else:
            # Form has validation errors
            messages.error(
                request,
                '⚠️ Please correct the errors in the comment form below.'
            )
    
    # Get approved comments
    comments = article.comments.filter(is_approved=True).order_by('-created_at')
    comments_count = comments.count()
    
    # Get related articles
    related_articles = NewsArticle.objects.filter(
        category=article.category,
        status='published'
    ).exclude(id=article.id).order_by('-published_at')[:3]
    
    # Prepare context
    context = {
        'article': article,
        'related_articles': related_articles,
        'comments': comments,
        'comment_form': comment_form,
        'comments_count': comments_count,
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