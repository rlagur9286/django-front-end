from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.shortcuts import resolve_url
from django.views.generic import DetailView, UpdateView, ListView, DeleteView, CreateView
from .models import Post, Comment
from django.views.decorators.csrf import csrf_exempt
import tensorflow as tf
from django.http import JsonResponse
import os

tf.app.flags.DEFINE_string("output_graph",
                           "blog/graph/output_graph.pb",
                           "학습된 신경망이 저장된 위치")
tf.app.flags.DEFINE_string("output_labels",
                           "blog/graph/output_labels.txt",
                           "학습할 레이블 데이터 파일")
FLAGS = tf.app.flags.FLAGS

labels = [line.rstrip() for line in tf.gfile.GFile(FLAGS.output_labels)]

with tf.gfile.FastGFile(FLAGS.output_graph, 'rb') as fp:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(fp.read())
    tf.import_graph_def(graph_def, name='')
config = tf.ConfigProto(allow_soft_placement=True)
sess = tf.Session(config=config)
logits = sess.graph.get_tensor_by_name('final_result:0')


index = ListView.as_view(model=Post, template_name='blog/index.html')

post_new = CreateView.as_view(model=Post, fields='__all__')

post_detail = DetailView.as_view(model=Post)

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
def check(request):
    file = request.FILES.get('img')

    fd = open('tmp.jpg', 'wb')
    for chunk in file.chunks():
        fd.write(chunk)
    fd.close()

    image = tf.gfile.FastGFile('tmp.jpg', 'rb').read()
    prediction = sess.run(logits, {'DecodeJpeg/contents:0': image})[0]

    print('=== 예측 결과 ===')

    if prediction[0] > prediction[1]:
        name = labels[0]
    else:
        name = labels[1]
    return JsonResponse({'success': True, 'result': name})


