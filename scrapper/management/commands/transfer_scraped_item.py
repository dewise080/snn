from django.core.management.base import BaseCommand
from scrapper.models import ScrapedItem, ScrapedItemImage
from website.models import ProductPage, ProductIndexPage
from wagtail.images.models import Image as WagtailImage
from django.utils.text import slugify
from django.utils import timezone
from django.db import transaction

class Command(BaseCommand):
    help = "Transfers up to 10 ScrapedItems to ProductPages under a ProductIndexPage, avoiding duplicates."

    def handle(self, *args, **options):
        # Check if ProductIndexPage exists (use Turkish version, locale_id=2)
        index_page = ProductIndexPage.objects.filter(locale_id=2).first()
        if not index_page:
            self.stdout.write(self.style.ERROR("No Turkish ProductIndexPage found. Please create one in the Wagtail admin with Turkish locale."))
            return

        # Get all existing ProductPage slugs to filter out already transferred items
        existing_slugs = set(ProductPage.objects.values_list('slug', flat=True))
        
        # Retrieve ScrapedItem entries that haven't been transferred yet
        untransferred_items = []
        for item in ScrapedItem.objects.all():
            potential_slug = slugify(f"{item.slug}-{item.id}")
            if potential_slug not in existing_slugs:
                untransferred_items.append(item)
                if len(untransferred_items) >= 10:
                    break
        
        if not untransferred_items:
            self.stdout.write(self.style.WARNING("No new ScrapedItems to transfer. All items have already been transferred."))
            return
        
        self.stdout.write(self.style.SUCCESS(f"Found {len(untransferred_items)} new items to transfer."))

        # Wrap in a transaction for atomicity
        with transaction.atomic():
            for scraped_item in untransferred_items:
                # Generate a unique and valid slug
                raw_slug = f"{scraped_item.slug}-{scraped_item.id}"
                slug = slugify(raw_slug)

                # Check if a ProductPage with the same slug already exists
                if ProductPage.objects.filter(slug=slug).exists():
                    self.stdout.write(self.style.WARNING(f"ProductPage for '{scraped_item.title}' already exists. Skipping."))
                    continue

                # Create ProductPage instance
                product_page = ProductPage(
                    title=scraped_item.title,
                    slug=slug,
                    price=scraped_item.price,
                    discount_price=scraped_item.discount_price,
                    description_short=scraped_item.description_short[:50] if scraped_item.description_short else "",
                    description_long=scraped_item.description_long or "",
                    first_published_at=timezone.now(),
                    last_published_at=timezone.now(),
                    show_in_menus=True,
                    locale_id=2,  # Set Turkish locale
                )

                # Add product_page as a child under ProductIndexPage
                index_page.add_child(instance=product_page)
                product_page.save_revision().publish()

                # Transfer associated images to StreamField
                scraped_images = ScrapedItemImage.objects.filter(item=scraped_item)
                image_data = []

                for scraped_image in scraped_images:
                    # Check if image is already in Wagtail's Image model
                    wagtail_image, created = WagtailImage.objects.get_or_create(
                        title=scraped_image.image.name,
                        defaults={'file': scraped_image.image}
                    )

                    # Append a dictionary with the proper format for StreamField
                    image_data.append({"type": "image", "value": wagtail_image.pk})

                # Assign the correctly formatted image data to the StreamField
                product_page.images = image_data
                product_page.save_revision().publish()

                self.stdout.write(self.style.SUCCESS(f"Successfully transferred '{scraped_item.title}' to ProductPage."))
