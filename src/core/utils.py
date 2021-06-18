from random import choice
from string import ascii_lowercase, digits

from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.text import slugify
from xhtml2pdf import pisa


def random_string_generator(size=10, chars=ascii_lowercase+digits):
    return ''.join(choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name)

    klass = instance.__class__
    qs_exists = klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = f'{slug}-{random_string_generator(size=5)}'
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def render_to_pdf(request, template_path, data, filename=None):
    response = HttpResponse(content_type='application/pdf')
    if filename is not None:
        response['Content-Disposition'] = f'inline; filename="{filename}_invoice.pdf"'
    else:
        response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    template = get_template(template_path)
    html = template.render(data)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return None
    return response
