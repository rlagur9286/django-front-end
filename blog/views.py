from django.urls import reverse_lazy
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import resolve_url
from django.views.generic import DetailView, UpdateView, ListView, DeleteView, CreateView
from django.views.decorators.csrf import csrf_exempt
from django.template.defaultfilters import truncatewords
from .serializers import PostSerializer
from rest_framework.renderers import JSONRenderer
from .models import Post, Comment


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_template_names(self):
        if self.request.is_ajax():
            return ['blog/_post_list.html']
        return ['blog/index.html']

index = PostListView.as_view()

post_new = CreateView.as_view(model=Post, fields='__all__')


class PostDetailView(DetailView):
    model = Post

    def render_to_response(self, context):
        # json 리스폰스
        if self.request.is_ajax():
            return JsonResponse({
                'title': self.object.title,
                'summary': truncatewords(self.object.content, 100),
            })
        # 템플릿 렌더링
        return super().render_to_response(context)

post_detail = PostDetailView.as_view()

post_edit = UpdateView.as_view(model=Post, fields='__all__')


class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/post_delete.html'

post_delete = PostDeleteView.as_view()


class CommentCreateView(CreateView):
    model = Comment
    fields = ['message']

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return resolve_url(self.object.post)

comment_new = CommentCreateView.as_view()


class CommentUpdateView(UpdateView):
    model = Comment
    fields = ['message']

    def get_success_url(self):
        return resolve_url(self.object.post)

comment_edit = CommentUpdateView.as_view()


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment_delete.html'

    def get_success_url(self):
        return resolve_url(self.object.post)

comment_delete = CommentDeleteView.as_view()


@csrf_exempt
def melon_search(request):
    return render(request, 'blog/melon_search.html')


def post_json(request):
    qs = Post.objects.all()

    serializer = PostSerializer(qs, many=True)
    json_utf8_string = JSONRenderer().render(serializer.data)

    return HttpResponse(json_utf8_string, content_type='application/json; charset=utf-8')
