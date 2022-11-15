# libraries
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

pd.set_option("display.max_columns",None)
pd.set_option("display.width",500)

sns.set(rc={"figure.figsize":(12,12)})


def create_user_df():
    movie = pd.read_csv("movie.csv")
    rating = pd.read_csv("rating.csv")

    # merging the data
    data = movie.merge(rating, how="left", on="movieId")

    comment_counts = pd.DataFrame(data["title"].value_counts())
    rare_movies = comment_counts[comment_counts["title"] <= 5000].index  # select less rated movies
    common_movies = data[~data["title"].isin(rare_movies)]  # the movies which are not less rates

    user_movie_df = common_movies.pivot_table(index=["userId"], columns=["title"], values="rating")

    return user_movie_df


def item_based_recommender(movie_name: str, user_movie_df):
    movie_name = user_movie_df[movie_name]

    return user_movie_df.corrwith(movie_name).sort_values(ascending=False).head(10)


def user_based_recommender(random_user, user_movie_df, ratio=0.90, cor_th=0.70, score=3.5):
    random_user_df = user_movie_df[user_movie_df.index == random_user]
    movies_watched = random_user_df.columns[random_user_df.notna().any()].tolist()

    movies_watched_df = user_movie_df[movies_watched]

    user_movie_count = movies_watched_df.T.notnull().sum()
    user_movie_count = user_movie_count.reset_index()
    user_movie_count.columns = ["userId", "movie_count"]

    percentage = len(movies_watched) * ratio

    users_with_same_movies = user_movie_count[user_movie_count["movie_count"] > percentage]["userId"]

    final_df = pd.concat([movies_watched_df[movies_watched_df.index.isin(users_with_same_movies)],
                          random_user_df[movies_watched]])

    correlation_df = final_df.T.corr().unstack().sort_values().drop_duplicates()
    correlation_df = pd.DataFrame(correlation_df, columns=["corr"])
    correlation_df.index.names = ["user_id_1", "user_id_2"]
    correlation_df = correlation_df.reset_index()

    top_users = correlation_df[(correlation_df["user_id_1"] == random_user) & (correlation_df["corr"] >= cor_th)][
        ["user_id_2", "corr"]].reset_index(drop=True)

    top_users = top_users.sort_values(by="corr", ascending=False)
    top_users.rename(columns={"user_id_2": "userId"}, inplace=True)

    rating = pd.read_csv("rating.csv")
    top_users_ratings = top_users.merge(rating[["userId", "movieId", "rating"]], how="inner")
    top_users_ratings["weighted_rating"] = top_users_ratings["corr"] * top_users_ratings["rating"]

    recommendation_df = top_users_ratings.groupby("movieId").agg({"weighted_rating": "mean"})
    recommendation_df = recommendation_df.reset_index()

    movies_to_be_recommended = recommendation_df[recommendation_df["weighted_rating"] > score].sort_values(
        "weighted_rating",
        ascending=False)

    movie = pd.read_csv("movie.csv")

    return movies_to_be_recommended.merge(movie[["movieId", "title"]])


user_movie_df = create_user_df()
user_movie_df = user_movie_df.astype(np.float32)
item_based_recommender("Avatar (2009)",user_movie_df)

random_user = int(pd.Series(user_movie_df.index).sample(1).values)
recommend_movies = user_based_recommender(random_user,user_movie_df)
print(recommend_movies)