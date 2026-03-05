from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0009_mediafile_allow_download'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemconfiguration',
            name='seo_canonical_base_url',
            field=models.URLField(
                blank=True,
                help_text='Tip: set your main domain, e.g., https://example.com',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='systemconfiguration',
            name='seo_default_meta_description',
            field=models.TextField(
                blank=True,
                help_text='Tip: write a clear summary in about 150-160 characters.',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='systemconfiguration',
            name='seo_default_meta_keywords',
            field=models.CharField(
                blank=True,
                help_text='Tip: comma-separated words (optional for modern SEO).',
                max_length=500,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='systemconfiguration',
            name='seo_default_meta_title',
            field=models.CharField(
                blank=True,
                help_text='Tip: keep title around 50-60 characters for search results.',
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='systemconfiguration',
            name='seo_meta_robots',
            field=models.CharField(
                default='index,follow',
                help_text='Tip: common values are index,follow or noindex,nofollow.',
                max_length=80,
            ),
        ),
        migrations.AddField(
            model_name='systemconfiguration',
            name='seo_og_image_url',
            field=models.URLField(
                blank=True,
                help_text='Tip: full image URL used for social sharing (Open Graph/Twitter).',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='systemconfiguration',
            name='seo_site_name',
            field=models.CharField(
                blank=True,
                help_text='Tip: your brand/site name (e.g., John Doe Portfolio).',
                max_length=120,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='systemconfiguration',
            name='seo_twitter_card',
            field=models.CharField(
                choices=[('summary', 'summary'),
                         ('summary_large_image', 'summary_large_image')],
                default='summary_large_image',
                help_text='Tip: use summary_large_image for better social previews.',
                max_length=30,
            ),
        ),
    ]
