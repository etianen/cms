from django import forms


from cms.apps.news.models import Article


class ArticleForm(forms.ModelForm):
    
    def clean(self):
        date = self.cleaned_data["publication_date"]
        url_title = self.cleaned_data["url_title"]
        try:
            article = Article.objects.get(publication_date__year=date.year,
                                          publication_date__month=date.month,
                                          url_title=url_title)
        except Article.DoesNotExist:
            return self.cleaned_data
        else:
            if article != self.instance:
                raise forms.ValidationError("An article with that date and URL title already exists.")
            return self.cleaned_data
    
    class Meta:
        model = Article