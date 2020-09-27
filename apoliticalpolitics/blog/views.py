from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .forms import CommentForm, SearchForm
from rcp import get_polls

from rcp import get_poll_data
from prettytable import PrettyTable


td = get_poll_data(
'https://www.realclearpolitics.com/epolls/2020/president/nc/north_carolina_trump_vs_biden-6744.html')

field_names = list(td[0]["data"][0].keys())
field_values = list(td[0]["data"][0].values())


#for row in td[0]["data"]:
#    x.add_row(row.values())
#print(x)


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 5
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments,'new_comment': new_comment, 'comment_form': comment_form})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'body')
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                search=search_vector, rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank')
    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})



battleground_states = [
    "Wisconsin",
    "Florida",
    "Pennsylvania",
    "Georgia",
    "North Carolina",
]


def poll_results(request):
    for state in battleground_states:
        polls = get_polls(candidate="Trump", state=state)
        for poll in polls:
            title = poll['poll'] 
            result = poll['result']
            print(title)
            print(result)
        print(state)
        print(field_values)
            
            
    return render(request, 'blog/polls.html', {'battleground_states': battleground_states, 'polls': polls, 'field_names': field_names, 'field_values': field_values})
