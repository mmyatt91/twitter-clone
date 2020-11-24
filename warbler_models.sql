CREATE TABLE "user" (
  "id" INT PRIMARY KEY,
  "email" TEXT UNIQUE NOT NULL,
  "username" TEXT UNIQUE NOT NULL,
  "image_url" TEXT DEFAULT '/static/images/default-pic.png',
  "header_image_url" TEXT DEFAULT '/static/images/warbler-hero.jpg',
  "bio" TEXT,
  "location" TEXT,
  "password" TEXT NOT NULL
);

CREATE TABLE "follows" (
  "user_being_followed_id" INT,
  "user_following_id" INT,
  PRIMARY KEY ("user_being_followed_id", "user_following_id")
);

CREATE TABLE "likes" (
  "id" INT PRIMARY KEY,
  "user_id" INT,
  "message_id" INT UNIQUE
);

CREATE TABLE "message" (
  "id" INT PRIMARY KEY,
  "text" STRING(140) NOT NULL,
  "timestamp" DATETIME NOT NULL,
  "user_id" INT NOT NULL
);

ALTER TABLE "user" ADD CONSTRAINT "follows_1" FOREIGN KEY ("id") REFERENCES "follows" ("user_being_followed_id") ON DELETE CASCADE;

ALTER TABLE "user" ADD CONSTRAINT "follows_2" FOREIGN KEY ("id") REFERENCES "follows" ("user_following_id") ON DELETE CASCADE;

ALTER TABLE "user" ADD CONSTRAINT "likes_1" FOREIGN KEY ("id") REFERENCES "likes" ("user_id") ON DELETE CASCADE;

ALTER TABLE "message" ADD CONSTRAINT "likes_2" FOREIGN KEY ("id") REFERENCES "likes" ("message_id") ON DELETE CASCADE;

ALTER TABLE "user" ADD CONSTRAINT "message" FOREIGN KEY ("id") REFERENCES "message" ("user_id") ON DELETE CASCADE;

