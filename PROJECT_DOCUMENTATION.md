# Project Documentation: Beauty Salon E-commerce Website

## 🎯 Project Overview
This is a **Django-based e-commerce website** for a beauty salon built with **Wagtail CMS** and **CodeRed Extensions**. The site includes:
- Multi-language support (English, Turkish, French)
- Product scraping capabilities from external sites (Procsin, Trendyol)
- E-commerce functionality with cart, checkout, and order management
- Custom content management through Wagtail

**Live Site**: http://www.beautysalon-nassnor.com

---

## 📦 Technology Stack

### Core Framework
- **Django 5.1.2** - Web framework
- **Wagtail 6.2.2** - CMS
- **CodeRed CMS 4.0.1** - Wagtail extensions
- **Python 3.10+** - Programming language

### Key Libraries
- **Playwright** - Browser automation for web scraping
- **BeautifulSoup4** - HTML parsing
- **Requests** - HTTP library
- **django-bootstrap5** - Frontend framework
- **wagtail-localize** - Translation management
- **Azure Translator** - Machine translation
- **SQLite** - Database (development)

---

## 🗂️ Project Structure

```
snn/
├── manage.py                    # Django management script
├── db.sqlite3                   # Database
├── requirements.txt             # Python dependencies
├── media/                       # User-uploaded files
│   ├── items/                   # Product images (organized by slug)
│   ├── categories/              # Category images
│   └── images/                  # General images
├── static/                      # Static assets (CSS, JS, images)
├── scrapper/                    # Web scraping app
│   ├── models.py               # Data models for scraped products
│   ├── views.py                # Views for scraping interface
│   ├── urls.py                 # URL routing
│   ├── admin.py                # Django admin configuration
│   ├── utils.py                # Scraping utility functions
│   ├── trendyol_scraper.py     # Trendyol-specific scraper
│   ├── wagtail_hooks.py        # Wagtail admin customizations
│   ├── templates/              # HTML templates
│   └── management/commands/    # Custom management commands
├── website/                     # Main website app
│   ├── models.py               # Wagtail page models
│   └── templates/              # Page templates
├── translations/                # Translation management app
│   ├── models.py
│   ├── views.py
│   └── azure.py                # Azure Translator integration
└── snn/                        # Project settings
    ├── settings/               # Settings split by environment
    │   ├── base.py            # Base settings
    │   ├── dev.py             # Development settings
    │   └── prod.py            # Production settings
    ├── urls.py                # Main URL configuration
    └── wsgi.py                # WSGI application
```

---

## 🔗 URL Structure & Routes

### Main URLs (`snn/urls.py`)

| URL Pattern | Description |
|------------|-------------|
| `/` | Homepage (Wagtail pages) |
| `/admin/` | Wagtail CMS admin panel |
| `/django-admin/` | Django admin panel |
| `/scrapper/` | Scraper web interface |
| `/scraper-panel/` | Custom scraper admin panel |
| `/docs/` | Wagtail documents |
| `/search/` | Search functionality |
| `/i18n/` | Language switcher |
| `/__debug__/` | Django Debug Toolbar (dev only) |

### Scrapper URLs (`scrapper/urls.py`)

| URL | View Function | Description |
|-----|---------------|-------------|
| `/scrapper/` | `scraped_list_view` | List all scraped products |
| `/scrapper/admin-panel/` | `scraper_admin_panel` | Scraper control panel (staff only) |
| `/scrapper/scrape-trendyol/` | `scrape_and_save_products` | Scrape Trendyol products |
| `/scrapper/scrape-procsin/` | `scrape_procsin_view` | Scrape Procsin products |
| `/scrapper/download-images/` | `download_images_for_scraped_items_view` | Download product images |
| `/scrapper/scrape-product-skus/` | `scrape_product_skus_view` | Generate product SKUs |
| `/scrapper/item/<id>/` | `scraped_item_detail_view` | View scraped item details |
| `/scrapper/create-product-page/<sku_id>/` | `create_product_page_view` | Create Wagtail page from SKU |

---

## 🛠️ Management Commands

### 1. **scrapselect** 
**File**: `scrapper/management/commands/scrapselect.py`

**Purpose**: Extract content from HTML files using XPath selectors

**Usage**:
```bash
python manage.py scrapselect [--website-ids ID1 ID2 ...]
```

**What it does**:
- Reads saved HTML files from `media/<website>/<date>/fullpage.html`
- Applies XPath selectors from `xpaths.csv`
- Extracts and saves content to `extracted_content.txt`
- Processes all websites or specific ones by ID

**Use case**: Extracting structured data from pre-downloaded HTML pages

---

### 2. **transfer_scraped_item**
**File**: `scrapper/management/commands/transfer_scraped_item.py`

**Purpose**: Transfer ScrapedItems to Wagtail ProductPages

**Usage**:
```bash
python manage.py transfer_scraped_item
```

**What it does**:
- Takes up to 10 `ScrapedItem` entries from the database
- Creates corresponding `ProductPage` entries in Wagtail
- Transfers product data (title, price, description, slug)
- Converts `ScrapedItemImage` to Wagtail images
- Adds pages as children of `ProductIndexPage`
- Publishes the pages automatically
- Avoids duplicates by checking slugs

**Requirements**:
- A `ProductIndexPage` must exist in Wagtail
- ScrapedItems must have valid data

---

### 3. **scrape_products**
**File**: `scrapper/management/commands/scrape_products.py`

**Purpose**: Generic product scraper with configurable options

**Usage**:
```bash
python manage.py scrape_products <URL> \
    --max_items 100 \
    --price_range 10-50 \
    --category TS,SB \
    --preview tabular \
    --driver_path /path/to/chromedriver \
    --headless
```

**Arguments**:
- `url`: Target e-commerce site URL
- `--max_items`: Maximum products to scrape (default: 100)
- `--price_range`: Filter by price (format: min-max)
- `--category`: Comma-separated category codes (SB, TS, SK, HS)
- `--preview`: Preview format (tabular or html)
- `--driver_path`: Path to ChromeDriver
- `--headless`: Run browser in headless mode

**What it does**:
- Uses Selenium WebDriver to scrape products
- Filters by price and category
- Generates preview (table or HTML file)
- Does NOT save to database (preview only)

---

### 4. **download_static_assets**
**File**: `scrapper/management/commands/download_static_assets.py`

**Purpose**: Download all CSS and JS files from a webpage

**Usage**:
```bash
python manage.py download_static_assets <URL> [--directory static/trendyol]
```

**Arguments**:
- `url`: URL of the page to download assets from
- `--directory`: Where to save files (default: static/trendyol)

**What it does**:
- Fetches the HTML of the target page
- Finds all `<link rel="stylesheet">` tags (CSS)
- Finds all `<script src="">` tags (JavaScript)
- Downloads each file to `static/<directory>/css/` or `js/`
- Useful for offline rendering or template creation

---

## 🤖 Web Scraping System

### Architecture

The scraping system has **two approaches**:

#### 1. **Direct Scraping → Database** (Procsin)
```
Web Page → Playwright → ScrapedItem → Database
                      ↓
                 Image Download → ScrapedItemImage
```

#### 2. **Scraping → SKU → Wagtail Page** (Procsin)
```
Web Page → Playwright → ProductSku → Manual Trigger → ProductPage (Wagtail)
                                                     ↓
                                              Image Download
```

---

### Scraping Functions (in `utils.py`)

#### **1. `scrape_procsin_products()`**
**Purpose**: Scrape product listings from Procsin

**What it does**:
- Uses Playwright in headless mode
- Navigates to `https://www.procsin.com/cilt-bakimi?ps=16&stock=1`
- Extracts: title, price, short description, image URL, product URL
- Generates slug from title
- Saves to `ScrapedItem` model
- Downloads and saves product images

**Run via**: 
- Web: POST to `/scrapper/scrape-procsin/`
- Runs in background thread

---

#### **2. `scrape_and_download_images()`**
**Purpose**: Download all images for existing ScrapedItems

**What it does**:
- Visits each `ScrapedItem.product_url`
- Finds gallery images (up to 12 per product)
- Downloads images using requests
- Saves to `media/items/<slug>/`
- Creates `ScrapedItemImage` entries
- Uses ThreadPoolExecutor (5 workers) for parallel processing
- Adds random delays (1-20 seconds) to avoid detection
- Batch saves every 5 images

**Run via**: 
- Web: `/scrapper/download-images/`

---

#### **3. `scrape_and_create_product_skus()`**
**Purpose**: Generate SKUs for products

**What it does**:
- Scrapes Procsin product listings
- Generates SKU format: `cilt-bakimi-MM-DD-XXX`
  - MM = month
  - DD = day
  - XXX = product index (001, 002, etc.)
- Saves to `ProductSku` model with:
  - Title
  - Price
  - SKU
  - constructed_urls (list of product URLs)

**Run via**: 
- Web: POST to `/scrapper/scrape-product-skus/`

---

#### **4. `create_product_page_from_sku(sku_instance)`**
**Purpose**: Create a full Wagtail ProductPage from a SKU

**What it does**:
1. Visits the product URL from the SKU
2. Scrapes:
   - Full product title
   - Price
   - Short description
   - Long description (full product body)
   - All gallery images (up to 12)
3. Downloads and saves images to Wagtail's Image library
4. Creates `ProductPage` with:
   - `slug` = SKU
   - `locale_id` = 2 (Turkish)
   - All scraped data
5. Adds page as child of `ProductIndexPage`
6. Publishes the page
7. Attaches images to StreamField

**Run via**: 
- Web: `/scrapper/create-product-page/<sku_id>/`
- Can be triggered from Wagtail admin for each SKU

---

#### **5. `scrape_trendyol_products(url, max_products=50)`**
**Purpose**: Scrape products from Trendyol

**What it does**:
- Uses Playwright (non-headless by default)
- Scrolls page to load more products
- Extracts: brand, name, price, image URL, product link
- Continues until `max_products` reached
- Returns list of product dictionaries
- Does NOT save to database automatically

**Run via**: 
- Web: POST to `/scrapper/scrape-trendyol/` with `url` parameter
- Saves to `ScrapedItem` model with `product_url` field

---

## 📊 Database Models

### Scrapper App Models

#### **ScrapedCategory**
Stores product categories
- `title`, `slug`, `description`
- `image` (ImageField)
- `is_active` (boolean)

#### **ScrapedItem**
Main scraped product model
- `title` - Product name
- `price` - Current price
- `discount_price` - Sale price (optional)
- `category` - ForeignKey to ScrapedCategory
- `label` - Sale/New/Promotion tag
- `slug` - URL-friendly identifier
- `stock_no` - Stock number
- `description_short` - Brief description
- `description_long` - Full description
- `image` - Main product image
- `is_active` - Visibility toggle
- `product_url` - Original source URL

#### **ScrapedItemImage**
Multiple images per product
- `item` - ForeignKey to ScrapedItem
- `image` - ImageField (stored in `media/items/<slug>/`)

#### **ProductSku**
SKU generation and tracking
- `title` - Product title
- `price` - Product price
- `sku` - Unique SKU code
- `constructed_urls` - JSONField with product URLs

#### E-commerce Models
- `ScrapedOrderItem` - Items in cart
- `ScrapedOrder` - Customer orders
- `ScrapedBillingAddress` - Shipping/billing info
- `ScrapedPayment` - Payment records
- `ScrapedCoupon` - Discount codes
- `ScrapedRefund` - Refund requests

---

### Website App Models (Wagtail Pages)

#### **HomePage** (extends CoderedWebPage)
- Hero section (background image, title, subtitle)
- Discount section (background, title, subtitle, description)
- Appointment info (address, phones, hours)

#### **ProductIndexPage** (extends CoderedWebPage)
- Parent page for all products
- Lists all ProductPage children
- Template: `product_index_page.html`

#### **ProductPage** (extends CoderedWebPage)
- Individual product page
- Fields: `price`, `discount_price`, `description_short`, `description_long`
- `images` - StreamField with ImageChooserBlock
- Parent must be ProductIndexPage
- Template: `product_page.html`

#### **Snippets** (Reusable content blocks)
- `ServiceSnippet` - Services offered
- `StaffSnippet` - Team members
- `WorkSnippet` - Portfolio items
- `PartnerSnippet` - Partner logos
- `PricingSnippet` - Price plans
- `CounterSnippet` - Statistics counters
- `FooterSnippet` - Footer content

#### Other Pages
- `ArticlePage` / `ArticleIndexPage` - Blog/news
- `EventPage` / `EventIndexPage` - Events calendar
- `LocationPage` / `LocationIndexPage` - Store locations
- `FormPage` - Contact forms
- `WebPage` - General content pages

---

## 🌍 Multi-language Support

### Configured Languages
1. **English** (en) - Default
2. **Turkish** (tr)
3. **French** (fr)

### Translation System
- **Wagtail Localize** - Content translation in CMS
- **Azure Translator** - Machine translation
  - Endpoint: `https://api.cognitive.microsofttranslator.com/`
  - Region: UAE North
  - Key: (configured in settings)

### Settings
```python
WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = [
    ('en', 'English'),
    ('tr', 'Turkish'),
    ('fr', 'French'),
]
WAGTAILLOCALIZE_MACHINE_TRANSLATOR = {
    "CLASS": "translations.azure.AzureTranslator",
    ...
}
```

### URLs
- `/i18n/` - Language switcher
- All CMS URLs wrapped in `i18n_patterns()`

---

## 🔐 Admin Panels

### 1. **Wagtail Admin** (`/admin/`)
- Full CMS control
- Page management
- Image library
- Snippets
- Settings
- Wagtail Localize (translations)
- Product SKU management (via wagtail-modeladmin)

### 2. **Django Admin** (`/django-admin/`)
- Direct database access
- Manage users
- ScrapedItem, ScrapedCategory management
- Order, Payment, Coupon management
- More technical/developer-focused

### 3. **Custom Scraper Panel** (`/scrapper/admin-panel/`)
- Staff-only interface
- Buttons to trigger scraping operations
- Monitor scraping status
- Template: `scraper_admin_panel.html`

---

## 🎨 Frontend & Templates

### Template Locations
- `scrapper/templates/` - Scraper-related pages
- `website/templates/` - Wagtail page templates
- `coderedcms/pages/` - Default CRX templates (can be overridden)

### Key Templates
| Template | Purpose |
|----------|---------|
| `scraper_admin_panel.html` | Custom scraper control panel |
| `scrapped_list.html` | List of scraped products |
| `scrapeditem_detail.html` | Single scraped product view |
| `product_page.html` | Wagtail product page |
| `product_index_page.html` | Product listing page |
| `home_page.html` | Homepage |

### Static Assets
- Bootstrap 5 (via django-bootstrap5)
- Custom CSS/JS in `static/`
- Debug Toolbar in development

---

## ⚙️ Settings Configuration

### Environment-based Settings
```
snn/settings/
├── base.py      # Common settings for all environments
├── dev.py       # Development-specific (DEBUG=True)
└── prod.py      # Production-specific (DEBUG=False)
```

### Key Settings (base.py)
```python
# Database
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}

# Time & Locale
TIME_ZONE = 'Europe/Istanbul'
LANGUAGE_CODE = 'en-us'

# Security
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'frame-ancestors': ["'self'", 'https://lona.beyond-board.me']
    }
}

# Media
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Static
STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "/static/"

# Wagtail
WAGTAIL_SITE_NAME = "Beauty"
WAGTAILADMIN_BASE_URL = "http://www.beautysalon-nassnor.com"
```

### Installed Apps (order matters)
1. Custom apps (`website`, `scrapper`, `translations`)
2. CodeRed CMS
3. Wagtail and extensions
4. Django core apps
5. Debug toolbar (dev only)
6. CSP (Content Security Policy)

---

## 🚀 Development Workflow

### Initial Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Create superuser
python manage.py createsuperuser

# 4. Collect static files
python manage.py collectstatic

# 5. Run development server
python manage.py runserver
```

### Common Tasks

#### Scraping Workflow
```bash
# Option A: Scrape and save directly
# 1. Visit /scrapper/scrape-procsin/ (POST request)
# 2. Visit /scrapper/download-images/ to get images

# Option B: Using SKUs (more controlled)
# 1. Visit /scrapper/scrape-product-skus/ (POST)
# 2. Go to Wagtail admin → Product SKUs
# 3. For each SKU, trigger /scrapper/create-product-page/<sku_id>/
```

#### Transfer Scraped Items to Wagtail
```bash
python manage.py transfer_scraped_item
```

#### Download Static Assets from a Site
```bash
python manage.py download_static_assets https://example.com --directory static/example
```

---

## 🐛 Debug & Development Tools

### Debug Toolbar
- Enabled in development (`DEBUG=True`)
- URL: `/__debug__/`
- Shows SQL queries, templates, cache, signals, etc.
- Custom middleware: `CustomDebugToolbarMiddleware`, `SuperuserDebugMiddleware`
- Only visible to superusers

### Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.error("Error message")
```

---

## 📈 Data Flow Examples

### Example 1: Procsin Product → Wagtail Page (Full Flow)

```
1. User clicks "Scrape Product SKUs" in /scrapper/admin-panel/
   ↓
2. POST to /scrapper/scrape-product-skus/
   ↓
3. scrape_and_create_product_skus() runs
   ↓
4. Playwright visits https://www.procsin.com/cilt-bakimi?ps=16&stock=1
   ↓
5. Extracts product data, generates SKU (cilt-bakimi-12-07-001)
   ↓
6. Saves to ProductSku model
   ↓
7. User goes to Wagtail admin → Product SKUs
   ↓
8. Clicks a SKU, then triggers /scrapper/create-product-page/<sku_id>/
   ↓
9. create_product_page_from_sku() runs:
   - Visits product URL
   - Scrapes full details + images
   - Creates ProductPage in Wagtail
   - Downloads images
   - Publishes page
   ↓
10. Product now live on website
```

### Example 2: Trendyol Quick Scrape

```
1. User submits form at /scrapper/admin-panel/ with Trendyol URL
   ↓
2. POST to /scrapper/scrape-trendyol/
   ↓
3. scrape_trendyol_products() runs
   ↓
4. Playwright scrolls and extracts products
   ↓
5. Creates ScrapedItem entries directly
   ↓
6. Products appear in /scrapper/ list view
   ↓
7. Optionally: Download images via /scrapper/download-images/
```

---

## 🔧 Customization Points

### Adding a New Scraper
1. Create function in `utils.py` or new file
2. Use Playwright or BeautifulSoup
3. Save to `ScrapedItem` or `ProductSku`
4. Add URL route in `scrapper/urls.py`
5. Create view function in `views.py`
6. Add button in `scraper_admin_panel.html`

### Adding New Product Fields
1. Update `ScrapedItem` model in `scrapper/models.py`
2. Update `ProductPage` model in `website/models.py`
3. Run `python manage.py makemigrations && python manage.py migrate`
4. Update scraping functions to capture new fields
5. Update `transfer_scraped_item.py` command
6. Update `create_product_page_from_sku()` function

### Adding New Languages
1. Add language to `WAGTAIL_CONTENT_LANGUAGES` in `settings/base.py`
2. Run `python manage.py migrate`
3. Update translations via Wagtail admin
4. Update Azure Translator settings if needed

---

## 📝 Important Notes

### Security
- CSP configured to allow iframe embedding from `lona.beyond-board.me`
- Debug toolbar only for superusers
- Staff-only decorator on scraper admin panel
- CSRF protection enabled

### Performance
- Wagtail Cache middleware active
- Image optimization via Willow
- Batch saving in scrapers (every 5 items)
- ThreadPoolExecutor for parallel image downloads

### Media Files
- Images saved with slugified names
- Organized by product: `media/items/<slug>/`
- Original images backed up in `media/original_images/`

### Best Practices
- Always create ProductIndexPage before transferring items
- Use SKU workflow for better control over Wagtail pages
- Monitor scraping logs for errors
- Add delays in scrapers to avoid IP bans
- Test scrapers on small batches first

---

## 🆘 Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'csp'"
```bash
pip install django-csp
```

#### "ProductIndexPage does not exist"
1. Go to Wagtail admin (`/admin/`)
2. Create a new page under Home
3. Choose "Product Index Page"
4. Save and publish

#### Scraper returns no products
- Check if site structure changed
- Update CSS selectors
- Check for CAPTCHA or bot detection
- Increase wait times in Playwright

#### Images not downloading
- Check `product_url` field is set on ScrapedItem
- Verify network connectivity
- Check media directory permissions
- Look for errors in console logs

#### Migrations fail
```bash
# Reset database (development only!)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 🎓 Learning Resources

- **Wagtail Docs**: https://docs.wagtail.io/
- **CodeRed CMS Docs**: https://docs.coderedcorp.com/wagtail-crx/
- **Django Docs**: https://docs.djangoproject.com/
- **Playwright Docs**: https://playwright.dev/python/
- **Bootstrap 5**: https://getbootstrap.com/

---

## 📞 Quick Reference

### Start Development Server
```bash
python manage.py runserver
```

### Access Admin
- Wagtail: http://localhost:8000/admin/
- Django: http://localhost:8000/django-admin/
- Scraper: http://localhost:8000/scrapper/admin-panel/

### Common Management Commands
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py transfer_scraped_item
python manage.py download_static_assets <URL>
```

### Database Location
```
/home/lofa/DEV-msi/snn/db.sqlite3
```

### Virtual Environment
```bash
source venv/bin/activate  # Activate
deactivate                # Deactivate
```

---

**Last Updated**: December 7, 2025
**Django Version**: 5.1.2
**Wagtail Version**: 6.2.2
**Python Version**: 3.10+
