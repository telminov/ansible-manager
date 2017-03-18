from core.generic.views import TemplateView


class Index(TemplateView):
    template_name = 'core/index.html'
    title = 'Ansible Manager Project'
index = Index.as_view()