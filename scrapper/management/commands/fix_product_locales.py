from django.core.management.base import BaseCommand
from website.models import ProductPage, ProductIndexPage


class Command(BaseCommand):
    help = "Fixes locale for ProductPages - moves them to Turkish locale and correct parent"

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-all',
            action='store_true',
            help='Delete all ProductPages instead of moving them',
        )

    def handle(self, *args, **options):
        if options['delete_all']:
            # Option 1: Delete all ProductPages
            count = ProductPage.objects.count()
            ProductPage.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {count} ProductPages. You can now run transfer_scraped_item to recreate them with correct locale."))
            return

        # Option 2: Fix existing ProductPages
        # Get Turkish index page
        turkish_index = ProductIndexPage.objects.filter(locale_id=2).first()
        
        if not turkish_index:
            self.stdout.write(self.style.ERROR("No Turkish ProductIndexPage found (locale_id=2). Please create one first."))
            return

        self.stdout.write(f"Found Turkish ProductIndexPage: {turkish_index.title} (ID: {turkish_index.id})")

        # Process all ProductPages
        moved_count = 0
        fixed_count = 0
        skipped_count = 0
        
        # Get all pages that need fixing (not Turkish or wrong parent)
        pages_to_fix = []
        for page in ProductPage.objects.all():
            parent = page.get_parent()
            needs_locale_fix = page.locale_id != 2
            needs_parent_fix = parent and parent.id != turkish_index.id
            
            if needs_locale_fix or needs_parent_fix:
                pages_to_fix.append(page)
        
        for page in pages_to_fix:
            parent = page.get_parent()
            
            # Check if already exists in Turkish locale with same slug
            if page.locale_id != 2:
                # Check for duplicate
                duplicate = ProductPage.objects.filter(
                    locale_id=2,
                    slug=page.slug
                ).exclude(id=page.id).first()
                
                if duplicate:
                    self.stdout.write(self.style.WARNING(f"  Skipping (duplicate exists): {page.title}"))
                    skipped_count += 1
                    continue
            
            # Move to correct parent if needed
            if parent and parent.id != turkish_index.id:
                try:
                    page.move(turkish_index, pos='last-child')
                    moved_count += 1
                    self.stdout.write(f"  Moved to Turkish index: {page.title}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Could not move {page.title}: {e}"))
                    continue
            
            # Fix locale if not Turkish (do this after moving to avoid conflicts)
            if page.locale_id != 2:
                try:
                    page.locale_id = 2
                    page.save()
                    fixed_count += 1
                    self.stdout.write(f"  Fixed locale for: {page.title}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Could not fix locale for {page.title}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\nCompleted:"))
        self.stdout.write(f"  - Fixed locale for {fixed_count} pages")
        self.stdout.write(f"  - Moved {moved_count} pages to correct parent")
        self.stdout.write(f"  - Skipped {skipped_count} duplicates")
        
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f"\nNote: {skipped_count} pages were skipped because Turkish versions already exist."))
            self.stdout.write("You may want to manually review and delete the English duplicates in Wagtail admin.")
        
        self.stdout.write(self.style.SUCCESS(f"\nAll ProductPages are now properly organized!"))
