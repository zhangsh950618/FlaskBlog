create table if not exists topic(
  topic_id integer PRIMARY KEY AUTO_INCREMENT,
  topic_name varchar(300) not null unique
);
create table if not exists post(
  post_id integer PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(300) not null unique,
  content text not null,
  post_time datetime not null,
  topic_id integer not null,
  FOREIGN KEY (topic_id) REFERENCES topic(topic_id)

);
create table if not exists tag(
  tag_id  integer PRIMARY KEY AUTO_INCREMENT,
  tag_name  varchar(300) not null unique
);
create table if not exists tag_record(
  tag_record_id integer PRIMARY KEY AUTO_INCREMENT,
  post_id integer not null,
  tag_id integer not null,
  FOREIGN KEY(post_id) REFERENCES post(post_id),
  FOREIGN KEY(tag_id) REFERENCES tag(tag_id)
);