CREATE TABLE IF NOT EXISTS pictures (
    id              integer      PRIMARY KEY AUTOINCREMENT,
    path            text         NOT NULL,
    right_answer    text,
    answer          text,
    typeof_dalton   text         NULL,
    is_recolored    integer      NULL
)