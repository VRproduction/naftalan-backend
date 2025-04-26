from django.urls import path
from . import views


urlpatterns = [
    path('hero-slider/', views.HeroSliderListView.as_view(), name='home-slider'),
    path('about-section/', views.AboutSectionView.as_view(), name='about-section'),
    path('sanatories-section/', views.SanatoriesSectionView.as_view(),
         name='sanatories-section'),
    path('sanatoriums/', views.SanatoriumsView.as_view(), name='sanatoriums'),
    path('treatments-section/', views.TreatmentsSectionView.as_view(),
         name='treatments-section'),
    path('packages-section/', views.PackagesSectionView.as_view(),
         name='packages-section'),
    path('customer-comments-section/',
         views.CustomerCommentsSectionView.as_view(),
         name='customer-comments-section'),
    path('customer-comments/', views.CustomerCommentsView.as_view(),
         name='customer-comments'),
    path('contact-section/', views.ContactSectionView.as_view(),
         name='contact-section'),
    path('blog-section/', views.BlogSectionView.as_view(), name='blog-section'),
    path('blogs/', views.BlogsView.as_view(), name='blogs'),
    path('faq-section/', views.FAQSectionView.as_view(), name='faq-section'),
    path('faq/', views.FAQView.as_view(), name='faq'),
]