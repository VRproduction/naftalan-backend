from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import (
    HeroSlider,
    AboutSection,
    SanatoriesSection,
    TreatmentsSection,
    PackagesSection,
    CustomerCommentsSection,
    CustomerComments,
    ContactSection,
    BlogSection,
    FAQSection,
    FAQ
)
from .serializers import (
    HeroSliderSerializer,
    AboutSectionSerializer,
    SanatoriesSectionSerializer,
    TreatmentsSectionSerializer,
    PackagesSectionSerializer,
    CustomerCommentsSectionSerializer,
    CustomerCommentsSerializer,
    ContactSectionSerializer,
    BlogSectionSerializer,
    FAQSectionSerializer,
    FAQSerializer
)


class HeroSliderListView(ListAPIView):
    queryset = HeroSlider.objects.all()
    serializer_class = HeroSliderSerializer


class AboutSectionView(RetrieveAPIView):
    serializer_class = AboutSectionSerializer

    def get_object(self):
        return AboutSection.objects.first()


class SanatoriesSectionView(RetrieveAPIView):
    serializer_class = SanatoriesSectionSerializer

    def get_object(self):
        return SanatoriesSection.objects.first()


class TreatmentsSectionView(RetrieveAPIView):
    serializer_class = TreatmentsSectionSerializer

    def get_object(self):
        return TreatmentsSection.objects.first()


class PackagesSectionView(RetrieveAPIView):
    serializer_class = PackagesSectionSerializer

    def get_object(self):
        return PackagesSection.objects.first()


class CustomerCommentsSectionView(RetrieveAPIView):
    serializer_class = CustomerCommentsSectionSerializer

    def get_object(self):
        return CustomerCommentsSection.objects.first()


class CustomerCommentsView(ListAPIView):
    queryset = CustomerComments.objects.all()
    serializer_class = CustomerCommentsSerializer


class ContactSectionView(RetrieveAPIView):
    serializer_class = ContactSectionSerializer

    def get_object(self):
        return ContactSection.objects.first()


class BlogSectionView(RetrieveAPIView):
    serializer_class = BlogSectionSerializer

    def get_object(self):
        return BlogSection.objects.first()


class FAQSectionView(RetrieveAPIView):
    serializer_class = FAQSectionSerializer

    def get_object(self):
        return FAQSection.objects.first()


class FAQView(ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer