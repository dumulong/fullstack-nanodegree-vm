        DELETE FROM "user";

        INSERT INTO "user" (email) VALUES
        ('dumulong@gmail.com'),
        ('joeshcmoe@gmail.com');


        DELETE FROM category;

        INSERT INTO category (id, name) VALUES
         ( 1, 'Soccer'),
         ( 2, 'Basketball'),
         ( 3, 'Baseball'),
         ( 4, 'Frisbee'),
         ( 5, 'Snowboarding'),
         ( 6, 'Rock Climbing'),
         ( 7, 'Football'),
         ( 8, 'Skating'),
         ( 9, 'Hockey');

        DELETE FROM category_item;


        INSERT INTO category_item (id, title, description, category_id, user_id) VALUES
        (1, 'Stick', 'Hockey Stick',  9, 1),
        (2, 'Goggles', 'Goggles',  5, 1),
        (3, 'Snowboard', 'Snowboard',  5, 1),
        (4, 'Two Shinguards', 'Two Shinguards',  1, 1),
        (5, 'Shinguards', 'Shinguards',  1, 1),
        (6, 'Frisbee', 'Frisbee',  4, 2),
        (7, 'Ball', 'Baseball Ball',  3, 1),
        (8, 'Jersey', 'Soccer Jersey',  1, 1),
        (9, 'Soccer Cleats', 'Soccer Cleats',  1, 1);
