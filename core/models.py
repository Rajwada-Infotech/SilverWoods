from django.db import models


class ProjectInfo(models.Model):
    name = models.CharField(max_length=200, default="Silverwoods")
    tagline = models.CharField(max_length=500, default="Luxury Living Redefined")
    description = models.TextField(default="")
    address = models.TextField(default="")
    city = models.CharField(max_length=100, default="")
    state = models.CharField(max_length=100, default="")
    pincode = models.CharField(max_length=10, default="")
    phone = models.CharField(max_length=20, default="")
    email = models.EmailField(default="info@silverwoods.com")
    website = models.URLField(blank=True)
    map_embed_url = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    director_name = models.CharField(max_length=200, default="")
    director_title = models.CharField(max_length=200, default="Managing Director")
    director_bio = models.TextField(default="")
    rera_number = models.CharField(max_length=100, blank=True)
    total_units = models.IntegerField(default=0)
    total_floors = models.IntegerField(default=0)
    total_towers = models.IntegerField(default=0)
    project_area = models.CharField(max_length=100, blank=True)
    possession_date = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = "Project Info"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class FlatType(models.Model):
    name = models.CharField(max_length=50)
    bhk = models.DecimalField(max_digits=3, decimal_places=1, default=1)
    carpet_area = models.CharField(max_length=50, default="", blank=True)
    buildup_area = models.CharField(max_length=50, default="", blank=True)
    terrace_area = models.CharField(max_length=50, default="", blank=True)
    super_buildup_area = models.CharField(max_length=50, default="", blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price_per_sqft = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'bhk']

    def __str__(self):
        return f"{self.bhk} BHK - {self.name}"


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default="star")
    description = models.CharField(max_length=300, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name


class Lead(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=20)
    flat_preference = models.CharField(max_length=50, blank=True)
    message = models.TextField(blank=True)
    source = models.CharField(max_length=50, default="website")
    popup_ad = models.ForeignKey('PopupAd', null=True, blank=True, on_delete=models.SET_NULL, related_name='leads')
    created_at = models.DateTimeField(auto_now_add=True)
    is_contacted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def get_source_display_label(self):
        labels = {
            'website': 'Website',
            'brochure': 'Brochure',
            'popup_ad': 'Popup Ad',
        }
        return labels.get(self.source, self.source.replace('_', ' ').title())

    def __str__(self):
        return f"{self.name} - {self.phone}"


class SiteVisitor(models.Model):
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    page_visited = models.CharField(max_length=500)
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visited_at']


class PopupAd(models.Model):
    title = models.CharField(max_length=200)
    image = models.FileField(upload_to="popups/", blank=True, null=True)
    description = models.TextField(blank=True)
    flat_type = models.CharField(max_length=50, blank=True)
    link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_external = models.BooleanField(default=False)
    project_logo = models.ImageField(upload_to="popups/logos/", blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class Review(models.Model):
    name = models.CharField(max_length=200)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    designation = models.CharField(max_length=100, blank=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating}★"


class BuildingFlat(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('reserved', 'Reserved'),
    ]
    tower = models.CharField(max_length=10, default="A")
    floor = models.IntegerField()
    flat_number = models.CharField(max_length=20)
    flat_type = models.ForeignKey(FlatType, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    class Meta:
        ordering = ['tower', 'floor', 'flat_number']
        unique_together = ['tower', 'flat_number']

    def __str__(self):
        return f"Tower {self.tower} - Floor {self.floor} - {self.flat_number}"


class VillaPlot(models.Model):
    STATUS_CHOICES = [
        ('available',    'Available'),
        ('sold',         'Sold'),
        ('reserved',     'Reserved'),
        ('not_for_sale', 'Not for Sale'),
    ]
    villa_no       = models.IntegerField(unique=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    owner_name     = models.CharField(max_length=200, blank=True)
    sold_at        = models.DateTimeField(null=True, blank=True)
    notes          = models.TextField(blank=True)
    reserved_by    = models.CharField(max_length=200, blank=True)
    reserved_until = models.DateTimeField(null=True, blank=True)
    completion_pct = models.IntegerField(default=0)

    class Meta:
        ordering = ['villa_no']

    def __str__(self):
        return f"Villa #{self.villa_no:03d} — {self.get_status_display()}"


class BrochureImage(models.Model):
    image = models.ImageField(upload_to="brochure/")
    order = models.IntegerField(default=0)
    caption = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Brochure Page {self.order}"


class ChatbotQA(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    keywords = models.CharField(
        max_length=500,
        help_text="Comma-separated keywords that trigger this question (e.g. price,cost,rate)"
    )
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Chatbot Q&A"
        verbose_name_plural = "Chatbot Q&As"

    def keyword_list(self):
        return [k.strip().lower() for k in self.keywords.split(',') if k.strip()]

    def __str__(self):
        return self.question[:80]
