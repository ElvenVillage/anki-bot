CREATE TABLE IF NOT EXISTS decks (
    deck_id INT NOT NULL PRIMARY KEY,
    deck_name VARCHAR(255) NOT NULL,
    deck_invite_link TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_decks (
    user_id BIGINT NOT NULL,
    deck_id INT NOT NULL,
    PRIMARY KEY(user_id, deck_id)
);

CREATE TABLE IF NOT EXISTS cards (
    card_id SERIAL NOT NULL PRIMARY KEY,
    deck_id INT NOT NULL REFERENCES decks(deck_id),
    front TEXT NOT NULL, 
    back TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS repetitions (
    rep_id SERIAL,
    user_id BIGINT NOT NULL,
    card_id BIGINT NOT NULL REFERENCES cards(card_id),
    latest_review DATE NOT NULL,
    progress INT NOT NULL,
    next_repeat DATE NOT NULL
);