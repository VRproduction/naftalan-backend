
from modeltranslation.translator import translator, TranslationOptions
from .models import Blog, BlogCategory, BlogTag

class BlogOptions(TranslationOptions):
    fields = ('title', 'description', 'short_description', 'meta_title', 'meta_description', 'meta_keywords') 

translator.register(Blog, BlogOptions)

class BlogCategoryOptions(TranslationOptions):
    fields = ('title',)

translator.register(BlogCategory, BlogCategoryOptions)

class BlogTagOptions(TranslationOptions):
    fields = ('title',)

translator.register(BlogTag, BlogTagOptions)