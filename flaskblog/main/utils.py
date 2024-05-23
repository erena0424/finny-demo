import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sqlalchemy import or_, and_
from flaskblog.models import Post, User, Review


def recommend_posts(user, num_neighbors):
    birthyear=user.birthdate.year
    # print(f'birthyear,{birthyear}')
    sym_users = User.query.filter(and_(or_(birthyear - 50 < birthyear, birthyear < birthyear - 50), User.gender==user.gender)).limit(10).all()
    print(sym_users)
    posts = Post.query.all() #get all posts
    # print(f'all_posts,{posts}')
    i = 3

    # make sure more than ten users total are registered.
    # while len(sym_users) < 10:
    #     i += 1
    #     sym_users = User.query.filter(and_(birthyear - 5*i < birthyear, birthyear < birthyear - 5*i, User.gender==user.gender)).limit(10).all()
    pd_sym_users = pd.DataFrame([{'sym_user_id': sym_user.id, 'gender': sym_user.gender, 'birthdate': sym_user.birthdate.year} for sym_user in sym_users])
    pd_sym_users.set_index('sym_user_id', inplace=True)
    # print(f'''{pd_sym_users}''')
    ratings_dict = {}
    
    # Loop through users and posts to populate the ratings
    for sym_user in sym_users:
        ratings_dict[sym_user.id] = {}
        for post in posts:
            reviews = Review.query.filter(and_(Review.post_id==post.id, Review.user_id==sym_user.id)).all()
            if reviews:
              rating=reviews[0].rating
              print(f'rating, {rating}')
            else:
                rating = 0  # You need to fetch the rating for the user and post here
            
            ratings_dict[sym_user.id][post.id]=rating

    # Create the DataFrame
    pd_posts = pd.DataFrame(ratings_dict)
    
    #recommended_posts_by_user= recommend_posts_by_user(user.id, 3, sym_users, posts) #get recommended posts based on symmilar users of the current user
    print(f'pd_sym_users.index.get_loc(user.id)', pd_sym_users.index.get_loc(user.id))
    print(f'user.id',user.id)
    print(f'num_neighbors',num_neighbors)
    print(f'pd_sym_users',pd_sym_users)
    print(f'pd_sym_users.values',pd_sym_users.values)
    print(f'pd_posts,{pd_posts}')
    recommended_posts_by_user = recommend_posts_by_user(user.id, num_neighbors, pd_sym_users, pd_posts)  # Get recommended posts based on similar users of the current user
    print(f'recommended_posts_by_user,{recommended_posts_by_user}')
    # Create a list to store recommended Post objects
    recommended_post_objects = []
    for post_id, predicted_rating in recommended_posts_by_user:
        post = Post.query.filter_by(id=post_id).first()
        print(post.id)
        # Check if the post exists
        if post:
            recommended_post_objects.append(post)
    print(recommended_post_objects)
    return recommended_post_objects

def recommend_posts_by_user(user, num_neighbors, us, df):
  df2 = df.copy()
  number_neighbors = num_neighbors
  
  knn = NearestNeighbors(metric='cosine', algorithm='brute')
  knn.fit(us.values)
  distances, indices = knn.kneighbors(us.values, n_neighbors=number_neighbors)
  print(f'indices,{indices}')
  # convert user_name to user
  user_index = df.columns.tolist().index(user)
  sim_users = indices[user_index].tolist()
  print(f'sim_users,{sim_users}')
  user_distances = distances[user_index].tolist()
  print(f'user_distances,{user_distances}')

  if user_index in sim_users:
    print(f'user_index,{user_index}')
    id_user = sim_users.index(user_index)
    print(f'id_user,{id_user}')
    sim_users.remove(user_index)
    user_distances.pop(id_user)
  else:
    sim_users = sim_users[:num_neighbors-1]
    user_distances = user_distances[:num_neighbors-1]
  
  # t: post_title, m: the row number of t in df
  # find posts without ratings by user
  for m,t in list(enumerate(df.index)):
    if df.iloc[m, user_index] == 0:

      # user_similarty = 1 - user_distance     
      user_similarity = [1-x for x in user_distances]
      user_similarity_copy = user_similarity.copy()
      nominator = 0

      # for each similar user
      for s in range(0, len(user_similarity)):

        # check if the rating by a similar user is zero
        if df.iloc[m, sim_users[s]] == 0:
          
          # if the rating is zero, ignore the rating and the similarity in calculating the predicted rating
          if len(user_similarity_copy) == (number_neighbors - 1):
            user_similarity_copy.pop(s)
          
          else:
            user_similarity_copy.pop(s-(len(user_similarity)-len(user_similarity_copy)))
            
        else:
          nominator = nominator + user_similarity[s]*df.iloc[m,sim_users[s]]
      
      # check if the number of the ratings with non-zero is positive
      if len(user_similarity_copy) > 0:

        # check if the sum of the ratings of the similar users is positive.
        if sum(user_similarity_copy) > 0:
          predicted_r = nominator/sum(user_similarity_copy)
        
        else:
          predicted_r = 0

      else:
        predicted_r = 0
        
      df2.iloc[m,user_index] = predicted_r
  print(f'df2,{df2}')
  #return df2.transpose().iloc[user]
  recommended_posts = []
  for m in df.index[(df.transpose().iloc[user_index] == 0)].tolist():
    print('m',m)
    index_df = df.index.tolist().index(m)
    predicted_rating = df2.iloc[index_df, user_index]
    print('predicted_rating',predicted_rating)
    recommended_posts.append((m, predicted_rating))

  #sorted_rm = sorted(recommended_posts, key=lambda x:x[1], reverse=True)
  recommended_posts = sorted(recommended_posts, key=lambda x: x[1], reverse=True)
  print('The list of the Recommended posts \n')
  for post in recommended_posts:
    print(f'{post}')
  return recommended_posts[:3]