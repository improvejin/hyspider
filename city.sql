CREATE TABLE `city_tb` (
  `id` int(11) unsigned NOT NULL,
  `g` char(1) NOT NULL DEFAULT '',
  `name` varchar(10) NOT NULL DEFAULT '',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `city_lm` (
  `id` int(11) unsigned NOT NULL,
  `g` char(1) NOT NULL DEFAULT '',
  `name` varchar(10) NOT NULL DEFAULT '',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `city_mt` (
  `id` int(11) unsigned NOT NULL,
  `g` char(1) NOT NULL DEFAULT '',
  `name` varchar(10) NOT NULL DEFAULT '',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `city` (
  `id_mt` int(11) NOT NULL,
  `id_tb` int(11) NOT NULL,
  `id_lm` int(11) NOT NULL,
  `g` char(255) NOT NULL,
  `name` varchar(10) CHARACTER SET utf8 NOT NULL,
  `fly` bit(1) NOT NULL DEFAULT b'0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_mt`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

replace city(id_mt, id_tb, id_lm, g, name)
select city_mt.id, city_tb.id, city_lm.id, city_mt.g, city_mt.name from city_mt join city_tb on city_mt.name=city_tb.name
join city_lm on city_mt.name=city_lm.name;