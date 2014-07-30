from django.db import models
from tinymce import models as tinymce_models


# Create your models here.

class StaticContent(models.Model):
    """
    All the static contents for the normal webpage
    """
    help_text = 'Waehle eines der folgenden Werte: <ul><li>"my.ortoloco" - Ankuendigungen auf my.ortoloco</li><li>"Willkommen" - ortolco - Homepage oben rechts</li><li>"HomeUnterMenu" - ortoloco-Homepage unten unterm Menu'
    name = models.CharField("Name", max_length=100, help_text=help_text)
    content = tinymce_models.HTMLField("Html-Inhalt", max_length=10000, default="")


    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        verbose_name = "Statischer Inhalt"
        verbose_name_plural = "Statische Inhalte"


class Media(models.Model):
    """
    All the medias that mentioned ortoloco
    """
    mediafile = models.FileField("Datei", upload_to='medias')
    name = models.CharField("Titel", max_length=200)
    year = models.CharField("Jahr", max_length=4)


    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        verbose_name = "Media"
        verbose_name_plural = "Medien"

class Download(models.Model):
    """
    All the downloads available on ortoloco.ch
    """
    mediafile = models.FileField("Datei", upload_to='downloads')
    name = models.CharField("Titel", max_length=200)


    def __unicode__(self):
        return u"%s" % (self.name)

    class Meta:
        verbose_name = "Download"
        verbose_name_plural = "Downloads"


class Link(models.Model):
    """
    All the links that are mentioned on ortoloco.ch
    """
    titel = models.CharField("Titel", max_length=200, default="Beispieltitel")
    link = models.CharField("Link", max_length=200, default="http://example.ch")
    description = models.CharField("Beschreibung", max_length=400)

    def __unicode__(self):
        return u"%s" % (self.titel)

    class Meta:
        verbose_name = "Link"
        verbose_name_plural = "Links"


class Document(models.Model):
    """
    All the documents that are available on ortoloco.ch
    """
    title = models.CharField("Titel", max_length=200, default="Beispieltitel")
    document = models.FileField("Dokument", upload_to='documents')
    description = models.CharField("Beschreibung", max_length=400)

    def __unicode__(self):
        return u"%s" % (self.title)

    class Meta:
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumente"


class Politoloco(models.Model):
    email = models.EmailField("E-Mail Adresse")

    def __unicode__(self):
        return u'Politoloco %s' % self.email

    class Meta:
        permissions = (('can_send_newsletter', 'Kann politoloco-Newsletter verschicken'),)