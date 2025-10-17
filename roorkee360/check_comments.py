#!/usr/bin/env python
"""
Comment Functionality Diagnostic Script
Run: python check_comments.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roorkee360.settings')
django.setup()

from news.models import NewsArticle, Comment, Category
from news.forms import CommentForm

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_models():
    """Check if models are working"""
    print_header("1. Checking Models")
    
    try:
        articles = NewsArticle.objects.filter(status='published')
        print(f"✅ Published articles: {articles.count()}")
        
        if articles.exists():
            article = articles.first()
            print(f"   First article: {article.title}")
            print(f"   Slug: {article.slug}")
            print(f"   URL: /article/{article.slug}/")
            
            comments = article.comments.all()
            print(f"   Total comments: {comments.count()}")
            print(f"   Approved comments: {article.comments.filter(is_approved=True).count()}")
            
            return article
        else:
            print("⚠️  No published articles found!")
            print("   Creating a test article...")
            
            # Create test category
            category, _ = Category.objects.get_or_create(
                name='trending',
                defaults={
                    'display_name': 'Trending',
                    'icon': 'fas fa-fire'
                }
            )
            
            # Create test article
            from django.contrib.auth.models import User
            user = User.objects.first() or User.objects.create_superuser(
                'admin', 'admin@test.com', 'admin123'
            )
            
            article = NewsArticle.objects.create(
                title="Test Article for Comments",
                slug="test-article-comments",
                content="This is a test article to check comment functionality.",
                category=category,
                author=user,
                status='published'
            )
            print(f"✅ Test article created: {article.title}")
            return article
            
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_forms():
    """Check if forms are working"""
    print_header("2. Checking Forms")
    
    try:
        from news.forms import CommentForm
        print("✅ CommentForm imported successfully")
        
        # Test with valid data
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'content': 'This is a test comment with more than ten characters.'
        }
        
        form = CommentForm(data)
        print(f"✅ Form created")
        print(f"   Valid: {form.is_valid()}")
        
        if form.is_valid():
            print(f"   ✅ Form validation passed!")
        else:
            print(f"   ❌ Form errors: {form.errors}")
        
        return True
    except ImportError as e:
        print(f"❌ Cannot import CommentForm: {e}")
        print("   Make sure news/forms.py exists!")
        return False
    except Exception as e:
        print(f"❌ Error checking forms: {e}")
        return False

def test_comment_creation(article):
    """Test creating a comment"""
    print_header("3. Testing Comment Creation")
    
    if not article:
        print("❌ No article available for testing")
        return False
    
    try:
        # Create test comment
        comment = Comment.objects.create(
            article=article,
            name="Diagnostic Test",
            email="diagnostic@test.com",
            content="This comment was created by the diagnostic script to verify functionality.",
            is_approved=True
        )
        
        print(f"✅ Comment created successfully!")
        print(f"   ID: {comment.id}")
        print(f"   Name: {comment.name}")
        print(f"   Approved: {comment.is_approved}")
        print(f"   Created: {comment.created_at}")
        
        # Verify it's retrievable
        retrieved = Comment.objects.get(id=comment.id)
        print(f"✅ Comment can be retrieved from database")
        
        return True
    except Exception as e:
        print(f"❌ Error creating comment: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_urls():
    """Check URL configuration"""
    print_header("4. Checking URLs")
    
    try:
        from django.urls import reverse
        
        # Test home URL
        try:
            home_url = reverse('news:home')
            print(f"✅ Home URL: {home_url}")
        except:
            print(f"❌ Cannot reverse 'news:home'")
        
        # Test article detail URL
        try:
            article_url = reverse('news:article_detail', kwargs={'slug': 'test-slug'})
            print(f"✅ Article detail URL pattern: {article_url}")
        except Exception as e:
            print(f"❌ Cannot reverse 'news:article_detail': {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error checking URLs: {e}")
        return False

def check_settings():
    """Check Django settings"""
    print_header("5. Checking Settings")
    
    from django.conf import settings
    
    # Check installed apps
    required_apps = [
        'django.contrib.sessions',
        'django.contrib.messages',
        'news'
    ]
    
    for app in required_apps:
        if app in settings.INSTALLED_APPS:
            print(f"✅ {app}")
        else:
            print(f"❌ {app} - MISSING!")
    
    # Check middleware
    required_middleware = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]
    
    print(f"\nMiddleware:")
    for mw in required_middleware:
        if mw in settings.MIDDLEWARE:
            print(f"✅ {mw.split('.')[-1]}")
        else:
            print(f"❌ {mw} - MISSING!")

def run_all_checks():
    """Run all diagnostic checks"""
    print("\n" + "="*60)
    print("  COMMENT FUNCTIONALITY DIAGNOSTIC TOOL")
    print("="*60)
    
    article = check_models()
    forms_ok = check_forms()
    
    if article and forms_ok:
        comment_ok = test_comment_creation(article)
    
    check_urls()
    check_settings()
    
    print_header("SUMMARY")
    
    if article and forms_ok:
        print("✅ All basic checks passed!")
        print(f"\n📝 Test article URL: /article/{article.slug}/")
        print("   Try opening this URL in browser and submit a comment")
    else:
        print("❌ Some checks failed. Review the output above.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    run_all_checks()