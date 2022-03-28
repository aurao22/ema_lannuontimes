DROP TABLE IF EXISTS `journal`;

CREATE TABLE IF NOT EXISTS `journal`(  
    `nom` TEXT NOT NULL PRIMARY KEY,
    `fondateur` TEXT,
    `frequence` TEXT,
    `site_web` TEXT,
    `url_articles` TEXT
);


DROP TABLE IF EXISTS `article`;

CREATE TABLE IF NOT EXISTS `article`(  
    `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `titre` TEXT NOT NULL,
    `date_parution` TEXT NOT NULL,
    `texte` TEXT NOT NULL,
    `auteur` TEXT,
    `tags` TEXT,
    `url` TEXT,
    `journal` TEXT NOT NULL,
    FOREIGN KEY(`journal`) references journal(`nom`)
);

