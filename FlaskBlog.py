# encoding=utf-8
import os
from flask import Flask, render_template, request, Markup, session, redirect, url_for, flash, g
import MySQLdb
from MySQLdb.cursors import DictCursor
import datetime
import markdown2
import jieba.analyse as analyse
import jieba.posseg as pseg
import sys
from analyse import sentiment
from snownlp import SnowNLP
import math
import re
from dao.blog_dao import BlogDao
import sys
from dao.comment_dao import *
from analyse.sentiment import *
import numpy as np
from analyse import cluster

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
app.config.from_object(__name__)  # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='siadfgjahguiew',
    USERNAME='MonsterCritic',
    PASSWORD='123'
))
UPLOAD_FOLDER = '/home/zsh/FlaskBlog/static/uploads'
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc',])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("select * from tag")
    tags = cursor.fetchall()
    return render_template("home.html", tags=tags)


@app.route('/post/<post_id>')
def post(post_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("select * from post where post_id = %s", (post_id,))
    post = cur.fetchone()
    post['content'] = Markup(markdown2.markdown(text=post['content'], extras=['fenced-code-blocks', 'tables'], ))
    return render_template('post.html', post=post)


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['passwd'] != app.config['PASSWORD']:
            error = 'Invalid password'
            return render_template('admin.html', error=error)
        else:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))

    if request.method == 'GET':
        if not session.get('logged_in'):
            return render_template('admin.html')
        else:
            return redirect(url_for('dashboard'))


@app.route('/logout', )
def admin_logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))


@app.route('/dashboard')
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))
    username = app.config['USERNAME']
    conn = get_db()
    cur = conn.cursor()
    cur.execute("select * from post,topic where post.topic_id = topic.topic_id")
    posts = cur.fetchall()
    # for post in posts:
    #     print post.
    return render_template('dashboard.html', posts=posts, is_posts=True)


@app.route('/topics')
def topics():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("select * from topic")
    topics = cur.fetchall()
    return render_template('dashboard.html', topics=topics, is_topics=True)


@app.route('/tags')
def tags():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("select * from tag")
    tags = cur.fetchall()
    return render_template('dashboard.html', tags=tags, is_tags=True)


@app.route('/tag/<tag_id>')
def tag(tag_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("select * from post,tag_record WHERE post.post_id = tag_record.post_id AND tag_id = %s", (tag_id,))
    posts_with_tag = cur.fetchall();
    return render_template("index.html", posts_with_tag=posts_with_tag)


@app.route('/temp')
def temp():
    return render_template("template.html")


@app.route('/topic/<topic_id>')
def topic(topic_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("select * from post where topic_id = %s", (topic_id,))
    posts_with_topic = cur.fetchall();
    return "hello"


@app.route('/c/imgUpload', methods=['get', 'post'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        print request.files
        if 'img' not in request.files:
            flash('No file part')
            print "No File"
            return redirect(request.url)
        file = request.files['img']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            file_dir = os.path.join(app.config['UPLOAD_FOLDER'])
            now = datetime.datetime.now()

            filename = str(now) + file.filename
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # print type(full_path)
            full_path = full_path.encode('utf-8')
            # print type(full_path)
            file.save(full_path)
            return "http://zhangshaohua.cc/static/uploads/" + filename


@app.route('/add_tag', methods=['post'])
def add_tag():
    added_tag_name = request.form['added_tag_name']
    conn = get_db()
    cur = conn.cursor()
    execute_sql_string = "insert into tag (tag_name) values(%s)"
    cur.execute(execute_sql_string, (added_tag_name,))
    cur.close()
    conn.commit()
    return redirect(url_for('tags'))


@app.route('/del_post/<post_id>', methods=['get'])
def del_post(post_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("delete from tag_record where post_id = %s", (post_id,))
    cur.execute("delete from post where post_id = %s", (post_id,))
    cur.close()
    conn.commit()
    return redirect(url_for('dashboard'))


@app.route('/del_tag/<tag_id>', methods=['get'])
def del_tag(tag_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("delete from tag_record where tag_id = %s", (tag_id,))
    cur.execute("delete from tag where tag_id = %s", (tag_id,))
    cur.close()
    conn.commit()
    return redirect(url_for('tags'))


@app.route('/add_topic', methods=['post'])
def add_topic():
    added_topic_name = request.form['added_topic_name']
    conn = get_db()
    cur = conn.cursor()
    execute_sql_string = "insert into topic (topic_name) values(%s)"
    cur.execute(execute_sql_string, (added_topic_name,))
    cur.close()
    conn.commit()
    return redirect(url_for('topics'))


@app.route('/del_topic/<topic_id>', methods=['get'])
def del_topic(topic_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("delete from post where topic_id = %s", (topic_id,))
    cur.execute("delete from topic where topic_id = %s", (topic_id,))
    cur.close()
    conn.commit()
    return redirect(url_for('topics'))


@app.route('/single', methods=['GET', 'POST'])
def single():
    content = u""
    if request.method == 'GET':
        content = u"12日上午，国家主席习近平同美国总统特朗普通电话。两国元首就朝鲜半岛局势等共同关心的问题交换了意见。习近平强调，中方坚持实现半岛无核化目标，坚持维护半岛和平稳定，主张通过和平方式解决问题，愿同美方就半岛问题保持沟通协调。关于叙利亚问题，习近平指出，任何使用化学武器的行为都不可接受。叙利亚问题要坚持政治解决的方向。联合国安理会保持团结对解决叙利亚问题非常重要，希望安理会发出一致声音。两国元首同意通过各种方式保持密切联系。"
    if request.method == 'POST':
        content = request.form['content']
    content = re.sub(u'(\s|\n|t)', u'', content)
    print content
    seg_list = [(word, flag) for word, flag in pseg.cut(content)]
    textrank_key_list = analyse.textrank(content, topK=5, withWeight=True)
    tf_idf_key_list = analyse.tfidf(content, topK=5, withWeight=True)
    s = sentiment.Sentiment()
    sentiment_score = s.single_review_sentiment_score(content)
    sentiment_score_up = (math.atan(sentiment_score) * 2 / math.pi + 1) / 2 * 100
    sentiment_score_down = 100 - sentiment_score_up
    s = SnowNLP(content)
    summary = s.summary(3)
    # print key_list
    # print("Default Mode: " + "/ ".join(seg_list))  # 精确模式
    return render_template("single.html",
                           seg_list=seg_list,
                           textrank_key_list=textrank_key_list,
                           tf_idf_key_list=tf_idf_key_list,
                           sentiment_score_up=sentiment_score_up,
                           sentiment_score_down=sentiment_score_down,
                           summary=summary,
                           content=content,
                           )


@app.route('/multi', methods=['GET', 'POST'])
def multi():
    b_dao = BlogDao()
    blogs = b_dao.search_blogs_with_limit(["郑爽"], 15)
    data = [[int(blog[5]), int(blog[6]), int(blog[7])] for blog in b_dao.search_blogs_with_limit(["Yeah虚拟小号"], 200)]
    blog = blogs[0]
    blog_id = blog[0]
    c_dao = CommentDao()
    comments = c_dao.search_all_comments_with_ids([blog_id])
    comments_data = []
    senti = Sentiment()
    for comment in comments:
        score = senti.single_review_sentiment_score(comment[3])
        comments_data.append((comment[3], score))

    return render_template("multi.html",
                           blogs=blogs,
                           data=data,
                           comments_data=comments_data
                           )


@app.route('/topic1', methods=['GET', 'POST'])
def topic1():
    b_dao = BlogDao()
    c_dao = CommentDao()
    senti = Sentiment()
    blogs = b_dao.search_blogs_with_limit(["郑爽", "Yeah虚拟小号"], 15)
    data = [[int(blog[5]), int(blog[6]), int(blog[7])] for blog in
            b_dao.search_blogs_with_limit(["郑爽", "Yeah虚拟小号"], 150)]
    all_blog_entities = cluster.get_classfied_blogs(["Yeah虚拟小号"], 2500, 0.5, 15)
    all_blog_entities.sort(key=lambda obj: max(obj, key=lambda ob: ob.get_hot_point()).get_post_time())
    scores = []
    post_times = []
    linechartdata = []
    for blog_entity in all_blog_entities:
        blog_ids = []
        for blog in blog_entity:
            blog_ids.append(blog.get_blog_id())
        comments = c_dao.search_all_comments_with_ids(blog_ids)
        score = 0
        for comment in comments:
            score += senti.single_review_sentiment_score(comment[3])
        most_hot_blog = max(blog_entity, key=lambda obj: obj.get_hot_point())
        # score /= len(comments)
        scores.append(score)
    for index, blog_entity in enumerate(all_blog_entities):
        most_hot_blog = max(blog_entity, key=lambda obj: obj.get_hot_point())
        post_times.append(str(most_hot_blog.get_post_time()))
        print most_hot_blog.get_post_time(), most_hot_blog.get_blog_info(), scores[index]
        # print type(str(most_hot_blog.get_blog_info()))
        linechartdata.append(
            {'author': most_hot_blog.get_author(), 'info': most_hot_blog.get_blog_info(), 'y': scores[index]})
    linechartdata = str(linechartdata).replace('u\'', '\'').decode("unicode-escape")
    topic_name = "郑爽"
    return render_template("topic1.html",
                           blogs=blogs,
                           data=data,
                           post_times=post_times,
                           linechartdata=linechartdata,
                           topic_name=topic_name)


@app.route('/topic2', methods=['GET', 'POST'])
def topic2():
    all_blog_entities = cluster.get_classfied_blogs(["央视春节联欢晚会"], 2500, 0.5, 15)
    print "get"
    b_dao = BlogDao()
    c_dao = CommentDao()
    senti = Sentiment()
    blogs = b_dao.search_blogs_with_limit(["央视春节联欢晚会"], 15)
    data = [[int(blog[5]), int(blog[6]), int(blog[7])] for blog in b_dao.search_blogs_with_limit(["央视春节联欢晚会"], 150)]
    all_blog_entities.sort(key=lambda obj: max(obj, key=lambda ob: ob.get_hot_point()).get_post_time())
    scores = []
    post_times = []
    linechartdata = []
    for blog_entity in all_blog_entities:
        blog_ids = []
        for blog in blog_entity:
            blog_ids.append(blog.get_blog_id())
        comments = c_dao.search_all_comments_with_ids(blog_ids)
        score = 0
        for comment in comments:
            score += senti.single_review_sentiment_score(comment[3])
        most_hot_blog = max(blog_entity, key=lambda obj: obj.get_hot_point())
        # score /= len(comments)
        scores.append(score)

    for index, blog_entity in enumerate(all_blog_entities):
        most_hot_blog = max(blog_entity, key=lambda obj: obj.get_hot_point())
        post_times.append(str(most_hot_blog.get_post_time()))
        print most_hot_blog.get_post_time(), most_hot_blog.get_blog_info(), scores[index]
        # print type(str(most_hot_blog.get_blog_info()))
        linechartdata.append({'info': most_hot_blog.get_blog_info(), 'y': scores[index]})
    linechartdata = str(linechartdata).replace('u\'', '\'').decode("unicode-escape")
    topic_name = "央视春节联欢晚会"
    return render_template("topic2.html",
                           blogs=blogs,
                           data=data,
                           post_times=post_times,
                           linechartdata=linechartdata,
                           topic_name=topic_name)


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'GET':
        conn = get_db()
        cur = conn.cursor()
        cur.execute("select * from tag")
        tags = cur.fetchall()
        cur.execute("select * from topic")
        topics = cur.fetchall()
        return render_template("add_post.html", tags=tags, topics=topics)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tag_ids = request.form.getlist('tag_ids')
        topic_id = request.form['topic_id']
        post_time = datetime.datetime.now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("insert into post (title,content,post_time,topic_id) values (%s,%s,%s,%s)",
                    (title, content, post_time, topic_id))
        conn.commit()
        cur.execute("select post_id from post where title = %s", (title,))
        post_id = cur.fetchone()['post_id']
        args = []
        for tag_id in tag_ids:
            args.append((post_id, tag_id))
        cur.executemany("insert into tag_record (post_id,tag_id) VALUES (%s,%s)", args)
        conn.commit()
        return redirect(url_for("post", post_id=post_id))


@app.route('/update_post/<post_id>', methods=['GET', 'POST'])
def update_post(post_id):
    if request.method == 'GET':
        conn = get_db()
        cur = conn.cursor()
        cur.execute("select * from tag")
        tags = cur.fetchall()
        cur.execute("select * from topic")
        topics = cur.fetchall()
        cur.execute("select * from post where post_id=%s", (post_id,))
        post = cur.fetchone()
        cur.execute("delete from tag_record where post_id=%s", (post_id,))
        conn.commit()
        return render_template("update_post.html", tags=tags, topics=topics, post=post)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tag_ids = request.form.getlist('tag_ids')
        topic_id = request.form['topic_id']
        post_time = datetime.datetime.now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("update post set title=%s,content=%s,post_time=%s,topic_id=%s WHERE post_id=%s",
                    (title, content, post_time, topic_id, post_id))
        conn.commit()
        # cur.execute("select post_id from post where title = %s", (title,))
        # post_id = cur.fetchone()['post_id']
        args = []
        for tag_id in tag_ids:
            args.append((post_id, tag_id))
        cur.executemany("insert into tag_record (post_id,tag_id) VALUES (%s,%s)", args)
        conn.commit()
        return redirect(url_for("post", post_id=post_id))


def connect_db():
    """Connects to the specific database."""
    conn = MySQLdb.connect(host="127.0.0.1",
                           user="root",
                           passwd="123",
                           db="graduation",
                           charset="utf8",
                           cursorclass=DictCursor)
    return conn


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = connect_db()
    return g.mysql_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'mysql_db'):
        g.mysql_db.close()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


if __name__ == '__main__':
    app.run(debug=True)
