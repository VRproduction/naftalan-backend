from rest_framework.generics import RetrieveAPIView, ListAPIView
from .models import About, History, TreatmentPage, TreatmentCategory, Treatment, TreatmentProcess, Indication, Contraindications
from .serializers import AboutSerializer, HistorySerializer, TreatmentPageSerializer, TreatmentCategorySerializer, TreatmentSerializer, TreatmentProcessSerializer, IndicationSerializer, ContraindicationsSerializer


class AboutView(RetrieveAPIView):
    serializer_class = AboutSerializer

    def get_object(self):
        return About.objects.first()


class HistoryView(RetrieveAPIView):
    serializer_class = HistorySerializer

    def get_object(self):
        return History.objects.first()


class TreatmentPageView(RetrieveAPIView):
    serializer_class = TreatmentPageSerializer

    def get_object(self):
        return TreatmentPage.objects.first()


class TreatmentCategoryView(ListAPIView):
    serializer_class = TreatmentCategorySerializer
    queryset = TreatmentCategory.objects.all()


class TreatmentListView(ListAPIView):
    serializer_class = TreatmentSerializer
    queryset = Treatment.objects.all()


class TreatmentProcessListView(ListAPIView):
    serializer_class = TreatmentProcessSerializer
    queryset = TreatmentProcess.objects.all()


class IndicationView(RetrieveAPIView):
    serializer_class = IndicationSerializer

    def get_object(self):
        return Indication.objects.first()


class ContraindicationsView(RetrieveAPIView):
    serializer_class = ContraindicationsSerializer

    def get_object(self):
        return Contraindications.objects.first()
