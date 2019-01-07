CREATE TABLE `match_cinema_lm2mt` (
  `id_mt` int(11) NOT NULL DEFAULT '0',
  `id_matched` int(11) NOT NULL DEFAULT '0',
  `match_type` tinyint(1) NOT NULL DEFAULT '0',
  `match_score` float NOT NULL DEFAULT '0',
  `match_step` tinyint(1) NOT NULL DEFAULT '0',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_mt`,`id_matched`),
  KEY `idx_id_mt` (`id_mt`) USING BTREE,
  KEY `idx_id_matched` (`id_matched`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8


CREATE TABLE `match_cinema_tb2mt` (
  `id_mt` int(11) NOT NULL DEFAULT '0',
  `id_matched` int(11) NOT NULL DEFAULT '0',
  `match_type` tinyint(1) NOT NULL DEFAULT '0',
  `match_score` float NOT NULL DEFAULT '0',
  `match_step` tinyint(1) NOT NULL DEFAULT '0',
  `is_delete` tinyint(1) NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_mt`,`id_matched`),
  KEY `idx_id_mt` (`id_mt`) USING BTREE,
  KEY `idx_id_matched` (`id_matched`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



1、通过phone匹配，结果不准确可能有两种情况导致：
    error1:phone相同但并不是同一cinema，同一品牌cinema不同地址phone可能相同, 此情况通过step3 AI检测出无效匹配并删除
    error2:同一cinema不同channel phone可能不同导致匹配不上, 此情况通过step2 AI匹配
2、通过AI匹配，通过AI将TB cinema未匹配上的在MT cinema中按区域查找匹配， AI匹配相对比较准确，但是BD有请求速度限制
3、删除无效匹配(一个id_mt匹配了多个id_tb, 一个id_tb匹配了多个id_mt)，通过AI检测地址相似度小于 0.85的删除
4、删除无效匹配后可能出现无匹配的TB cinema, 此时需重复step2通过AI进行匹配


总结：初略匹配(phone, AI)->删除无效匹配(AI)->未匹配上的进行AI匹配


DELETE from cinema;
insert into cinema(name, addr, city, district, phone, lng_lat, confidence, id_mt, id_tb, match_type_mt_tb, match_score_mt_tb, is_delete
select cinema_mt.name, cinema_mt.addr, cinema_mt.city, cinema_mt.district, cinema_mt.phone, IF(cinema_mt.confidence>cinema_tb.confidence, cinema_mt.lng_lat, cinema_tb.lng_lat),
IF(cinema_mt.confidence>cinema_tb.confidence, cinema_mt.confidence,cinema_tb.confidence),  cinema_mt.id, cinema_tb.id, 1, 1, 0
from cinema_mt join cinema_tb on
(cinema_mt.phone = cinema_tb.phone)
OR
(INSTR(cinema_mt.addr,cinema_tb.addr)>0 or INSTR(cinema_tb.addr,cinema_mt.addr)>0)
OR
((INSTR(cinema_mt.name,cinema_tb.name)>0 or INSTR(cinema_tb.name,cinema_mt.name)>0) and cinema_mt.district=cinema_tb.district)



-- 可能不同的影院电话号码一样，需手动处理
select *from cinema join cinema_tb on cinema.id_tb = cinema_tb.id
where id_mt in (
select id_mt from cinema
group by id_mt
HAVING count(*) > 1
)


select cinema.id, cinema.is_delete, cinema.addr, cinema_tb.name,id_mt, id_tb ,  cinema_tb.addr from cinema join cinema_tb on cinema.id_tb = cinema_tb.id
where id_mt in (
select id_mt from cinema where is_delete = 0
group by id_mt
HAVING count(*) > 1
)
and  cinema.match_type_mt_tb = 1 and is_delete=0
order by id_mt


select cinema.id, cinema.is_delete, cinema.addr, cinema_tb.name,id_mt, id_tb ,  cinema_tb.addr from cinema join cinema_tb on cinema.id_tb = cinema_tb.id
where id_tb in (
select id_tb from cinema where is_delete = 0
group by id_tb
HAVING count(*) > 1
)
and  cinema.match_type_mt_tb = 1 and is_delete=0
order by id_tb


select cinema.id, cinema.addr, cinema_tb.addr from cinema join cinema_tb on cinema.id_tb = cinema_tb.id
where is_delete=1

select * from cinema_tb left join cinema  on cinema.id_tb = cinema_tb.id and cinema.is_delete=0
where cinema.id is null