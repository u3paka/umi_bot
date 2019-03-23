/// <reference path="typings/node/node.d.ts" />
// declare function require(x: string): any;
require('es6-promise').polyfill();
var Promise = require('es6-promise').Promise;
console.log('UmiA_Stream.js starting...');
// +++++++++++++++++//
/// 基本依存MODULE /////
// +++++++++++++++++//
var fs = require('fs');
var os = require('os');
var exec = require('child-process-promise').exec;
var spawn = require('child-process-promise').spawn;
var promiseRetry = require('promise-retry');
var request = require('request');
var _ = require('lodash');
// Twitter-module
var twitter = require('twitter');
var MsTranslator = require('mstranslator');
/////////////////////
var Sequelize = require('sequelize');
// +++++++++++++++++//
/// DBグローバル変数/////
// +++++++++++++++++//
var GLOBAL_VALs = (select:string) => {
	//適当
	if (os.cpus()[0].speed == 2700) {
		var PROJECT_PLACE = '/Users/xxxx';
	} else { 
		PROJECT_PLACE = '/mnt/usbstorage/umiA';
		// PROJECT_PLACE = '/media/pi/16G4RPI/umiA'; 
	};
	//
	switch (select) {
		case 'SECRET_DIC_PLACE':
			var ret = PROJECT_PLACE + '/Data/secretDict.json';
			break;
		case 'DB_PLACE':
			var ret = PROJECT_PLACE + '/umiA.sqlite3';
			break;
		case 'Dics_PLACE':
			var ret = PROJECT_PLACE + '/Data/Dics.json';
			break;
		case 'MECAB_CMD':
			var ret = 'mecab -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd';
			break;
		default:
			var ret = PROJECT_PLACE;
	};
	return ret;
};
var PROJECT_PLACE = GLOBAL_VALs('PROJECT_PLACE');
var SECRET_DIC_PLACE = GLOBAL_VALs('SECRET_DIC_PLACE');
var DB_PLACE = GLOBAL_VALs('DB_PLACE');
var TweetsDB_PLACE = GLOBAL_VALs('TweetsDB_PLACE');
var Dics_PLACE = GLOBAL_VALs('Dics_PLACE');
var PYTHON = '/Users/xxxx';
var MECAB_CMD = '/usr/local/bin/mecab -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd';
var SQLplace = '/Users/xxxx';
var TWTRDataplace = '/Users/xxxx';
// } else {
// 	PYTHON = '/opt/conda/bin/python';
// 	MECAB_CMD = 'mecab -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd';
// 	SQLplace = '/mnt/usbstorage/umiA/umiA.sqlite3';
// 	TWTRDataplace = '/mnt/usbstorage/umiA/twtrData.sqlite3';
// };
var tryNum = 0;
// +++++++++++++++++++++++++//
/// READ EXTERNAL DATABASEs/////
// +++++++++++++++++++++++++//
var SECRETDIC = JSON.parse(fs.readFileSync(SECRET_DIC_PLACE, 'utf8'));
var Dics = JSON.parse(fs.readFileSync(Dics_PLACE, 'utf8'));

var eStat_API_ID = SECRETDIC['e-Stat_API_ID'];
var plotlyAPIKEY = SECRETDIC['plotlyAPIKEY'];
var plotlyStreamToken = SECRETDIC["plotlyStreamToken"];
// var DAPIKEY = SECRETDIC["Docomo_API_KEY"];
var DAPIKEY = SECRETDIC["Docomo_API_KEY1"];
var YAPIKEY = SECRETDIC["YahooAPI"];
var UmiphrasesList = Dics.Umiphrases;
var PSphraseList = Dics.PSphrases;
// +++++++++++++++++//
/// MODULE IMPORT/////
// +++++++++++++++++//
var sequelize = new Sequelize('users', '', '', {
	dialect: 'sqlite',
	pool: {
    max: 5,
    min: 0,
    idle: 10000
  },
	storage: SQLplace,
	logging: false
});
var sequelizeTWTR = new Sequelize('twitter', '', '', {
	dialect: 'sqlite',
	pool: {
    max: 5,
    min: 0,
    idle: 10000
  },
	storage: TWTRDataplace,
	logging: false
});
sequelize.transaction({
		// autocommit :false,
		isolationLevel: Sequelize.Transaction.READ_COMMITTED || "READ COMMITTED"
	}).then((trnPRAGMA) => {
		sequelize.query('PRAGMA journal_mode = PERSIST').then((result) => {
		    console.log(result);
		});
		sequelize.query('PRAGMA synchronous = OFF').then((result) => {
		    console.log(result);
		});
		// trnPRAGMA.commit();
	});
sequelizeTWTR.transaction({
		// autocommit :false,
		isolationLevel: Sequelize.Transaction.READ_COMMITTED || "READ COMMITTED"
	}).then((trnTPRAGMA) => {
		sequelizeTWTR.query('PRAGMA journal_mode = PERSIST').then((result) => {
		    console.log(result);
		});
		sequelizeTWTR.query('PRAGMA synchronous = OFF').then((result) => {
		    console.log(result);
		});
		// trnPRAGMA.commit();
	});
var User = sequelize.define('users', {
		screen_name: {
			type: Sequelize.STRING,
			field: 'screen_name', // Will result in an attribute that is firstName when user 	facing but first_name in the database
			unique: true,
			primaryKey: true,
		},
		usr_id: Sequelize.STRING,
		name: Sequelize.STRING,
		context: Sequelize.STRING,
		mode: Sequelize.STRING,
		auth: Sequelize.STRING,
		time: Sequelize.STRING,
		recentID: Sequelize.STRING,
		cnt: Sequelize.INTEGER,
		replycnt: Sequelize.INTEGER,
		totalcnt: Sequelize.INTEGER,
		waiting: Sequelize.STRING,
		exp: Sequelize.INTEGER,
		other: Sequelize.STRING,
		friends_cnt: Sequelize.INTEGER,
		followers_cnt: Sequelize.INTEGER,
		statuses_cnt: Sequelize.INTEGER,
		fav_cnt: Sequelize.INTEGER,
		status_id: Sequelize.STRING,
		reply_id: Sequelize.STRING,
		reply_name: Sequelize.STRING
	},
	{
			freezeTableName: true // Model tableName will be the same as the model 	name
	}
);
// +++++++++++++++++//
/// PHRASEs DATABASE/////
// +++++++++++++++++//
var Phrases = sequelize.define('phrases', {
		phrase: {
			type: Sequelize.STRING,
			unique: true,
			primaryKey: true,
		},
		framework: Sequelize.STRING,
		s_type : Sequelize.STRING,
		status: Sequelize.STRING,
		react_sense: Sequelize.STRING,
		react_keyword: Sequelize.STRING,
		field_info: Sequelize.STRING,
		area_info: Sequelize.STRING,
		character: Sequelize.STRING,
		ok_cnt: Sequelize.INTEGER,
		ng_cnt: Sequelize.INTEGER,
		author: Sequelize.STRING
	},{
			freezeTableName: true // Model tableName will be the same as the model 	name
	}
);
var ERRphrase = {phrase:'...', s_type:'error'};
var getPhrase = (query = {character: 'U'}, ERRans = ERRphrase  ) => {
	return sequelize.transaction({
		// autocommit :false,
		isolationLevel: Sequelize.Transaction.READ_COMMITTED || "READ COMMITTED"
	}).then((trnGP) => {
		return promiseRetry({retries: 1},(retry, tryNum) => {
			return Phrases.findAll({ where: query, transaction: trnGP})
			.then((result) => {
				return Promise.resolve(result);
			}).catch(retry);
		}).then((result) => {
			trnGP.commit();
			if (result != []){
				var phrase = _.sample(result);
				return Promise.resolve(phrase['dataValues']);
			} else {
				return Promise.resolve(ERRans);
			};
		}).catch((e) => {
			if(trnGP != undefined){
				// console.log(trnGP)
				trnGP.rollback()
			};
  			console.log('[ERR][get.Phrase][' + tryNum + '] ' + query);
			console.log(e)
			return Promise.resolve(ERRans);
		});
	}).catch((e) => {
		console.log(e);
		return Promise.resolve(ERRans);
	});
};
var savePhrase = (info) => {
	// return sequelize.sync({force: true})
	// .then(() => {
	return sequelize.transaction({
		// autocommit :false,
		isolationLevel: Sequelize.Transaction.READ_COMMITTED || "READ COMMITTED"
	}).then((trnSP) => {
		var tryNum = 0;
		return promiseRetry({retries: 1},(retry, tryNum) => {
			return Phrases.upsert(info)
			.then((result) => {
				trnSP.commit();
				console.log('[OK][upsert.Phrase][' + tryNum + '] ' + info.phrase);
				return Promise.resolve(info);
			}).catch(retry);
		}).catch((e) => {
			if(trnSP != undefined){
				trnSP.rollback();
			};
  			console.log('[ERR][upsert.Phrase][' + tryNum + '] ' + info.phrase);
			console.log(e)
			return Promise.resolve({});
		});
	});
};

// var twsequelize = new Sequelize('tweets', '', '', { dialect: 'sqlite', storage: './tweets.sqlite3' });
var TweetSQL = sequelizeTWTR.define('tweets', {
	screen_name: Sequelize.STRING,
	name: Sequelize.STRING,
	user_id: Sequelize.STRING,
	text: Sequelize.STRING,
	bot_id: Sequelize.STRING
});

var DirectMessageSQL = sequelizeTWTR.define('dms', {
	screen_name: Sequelize.STRING,
	name: Sequelize.STRING,
	user_id: Sequelize.STRING,
	text: Sequelize.STRING,
	bot_id: Sequelize.STRING
});
var getSQLTweet = (query = {}, ERRans = ERRphrase) => {
	return sequelizeTWTR.transaction({
		// autocommit :false,
		isolationLevel: Sequelize.Transaction.READ_COMMITTED || "READ COMMITTED"
	}).then((trnGP) => {
		return promiseRetry({retries: 1},(retry, tryNum) => {
			return TweetSQL.findOne({ where: query, transaction: trnGP})
			.then((result) => {
				return Promise.resolve(result);
			}).catch(retry);
		}).then((result) => {
			// console.log(result)
			// console.log(result['dataValues'])
			trnGP.commit();
			if (result != []){
				// var phrase = _.sample(result);
				return Promise.resolve(result['dataValues']);
			} else {
				return Promise.resolve(ERRans);
			};
		}).catch((e) => {
			if(trnGP != undefined){
				// console.log(trnGP)
				trnGP.rollback()
			};
  			console.log('[ERR][get.Phrase][' + tryNum + '] ' + query);
			console.log(e)
			return Promise.resolve(ERRans);
		});
	}).catch((e) => {
		console.log(e);
		return Promise.resolve(ERRans);
	});
};
var twtrSECRETU = SECRETDIC["twtr"]['Umi'];
var twtrSECRETR = SECRETDIC["twtr"]['Rin'];
var twtrSECRETE = SECRETDIC["twtr"]['Exp']; //suspended only read...
//Umibot
var twtrU = new twitter({
	"access_token_key": twtrSECRETU["access_token_key"],
	"access_token_secret": twtrSECRETU["access_token_secret"],
	"consumer_key": twtrSECRETU["consumer_key"],
	"consumer_secret": twtrSECRETU["consumer_secret"]
});
//Rinbot
var twtrR = new twitter({
	"access_token_key": twtrSECRETR["access_token_key"],
	"access_token_secret": twtrSECRETR["access_token_secret"],
	"consumer_key": twtrSECRETR["consumer_key"],
	"consumer_secret": twtrSECRETR["consumer_secret"]
});
var twtrE = new twitter({
	"access_token_key": twtrSECRETE["access_token_key"],
	"access_token_secret": twtrSECRETE["access_token_secret"],
	"consumer_key": twtrSECRETE["consumer_key"],
	"consumer_secret": twtrSECRETE["consumer_secret"]
});

var MeCab = require('mecab-async');
var mecab = new MeCab();
MeCab.command = MECAB_CMD;

// var plotlyUSERNAME = 'xxxx';
// var plotly = require('plotly')(plotlyUSERNAME, plotlyAPIKEY);

var MSTclient = new MsTranslator({
	client_id: "_umiA"
	, client_secret: SECRETDIC["MSTranslate"]
}, true);

var translate = (text, to = 'ja') => {
	return new Promise((resolve, reject) => {
		var params = {
			text: text,
			to: 'ja'
		};
		params.to = to;
		MSTclient.translate(params, (err, data) => {
			if (err) { resolve(text) };
			resolve(data);
		});
	}).catch((e) => {
		console.log(e)
		return Promise.resolve('翻訳に失敗しました。');
	})
};
var detectLang = (text) => {
	return new Promise((resolve, reject) => {
		var params = {
			text: text
		};
		MSTclient.detect(params, (err, data) => {
			if (err) { reject(text) };
			resolve(data);
		});
	}).catch((e) => {
		console.log(e)
		return Promise.resolve('何語かわかりませんでした。');
	})
};
// +++++++++++++++++//
/// PYTHON MODULE/////
// +++++++++++++++++//
var spawnbase = (cmd:string, param = []) => {
	return new Promise((resolve, reject) => {
		resolve();
	}).then(() => {
		var result = '';
		var error = '';
		return spawn(cmd, param)
			.progress((childProcess) => {
				console.log('[spawn] childProcess.pid: ', childProcess.pid);
				childProcess.stdout.on('data', (data) => {
					result = data.toString();
				});
				childProcess.stderr.on('data', (data) => {
					error = data.toString();
				});
			}).then(() => {
				console.log('[spawn] done!');
				return Promise.resolve(result);
			}).catch((err) => {
				console.error('[spawn] ERROR: ', err, error);
				return Promise.reject(err);
			});
	});
};

var print = (str, isShow = true) => {
	if(isShow){console.log(str);}
};

// spawnbase('sudo',['reboot']).then((r) => { console.log(r);});
var spawnPy3 = (filename: string, text: string, pyfunc: string) => {
	return spawnbase(PYTHON, [filename, text, pyfunc]);
};
var spawnPM2 = (cmd: string = 'restart', arg: string = 'all') => {
	return spawnbase('pm2', [cmd, arg]);
};
var runUmibotPy = (callback) => {
	this.UMI_PLACE = PROJECT_PLACE + '/Python3/Umi_bot_ver5.py';
	exec('python ' + this.UMI_PLACE, (err, stdout, stderr) => {
		callback(err, stdout, stderr);
	});
};

var SyA_py = (text: string, 	pyfunc:string = 'SyA.showPairs()') => {
	var filename = PROJECT_PLACE + '/Python3/syntacticAnalysis.py';
	return spawnPy3(filename, text, pyfunc);
}; 

var ISM_py = (text: string, pyfunc: string = 'ISM()') => {
	var filename = PROJECT_PLACE + '/Python3/ISM.py';
	return spawnPy3(filename, text, pyfunc);
};

var twmon_py = (text: string, pyfunc: string = 'status()') => {
	var filename = PROJECT_PLACE + '/Python3/twmon.py';
	return spawnPy3(filename, text, pyfunc);
};

var shiritori_py = (text: string, name: string = 'xxxx') => {
	var filename = PROJECT_PLACE + '/Python3/shiritori.py';
	return spawnPy3(filename, text, name);
};

var TFIDF_py = (text: string, command: string = 'return') => {
	var filename = PROJECT_PLACE + '/Python3/TFIDF.py';
	return spawnPy3(filename, text, command);
};

var trigram_py = (text: string = '', command: string = 'return') => {
	var filename = PROJECT_PLACE + '/Python3/trigramMC.py';
	return spawnPy3(filename, text, command);
};

var createTweet_py = (text: string, name: string = 'xxxx') => {
	var filename = PROJECT_PLACE + '/Python3/createTweet.py';
	return spawnPy3(filename, text, name);
};

var assessSHF_py = (text: string, name: string = 'xxxx') => {
	var filename = PROJECT_PLACE + '/Python3/assessSHF.py';
	return spawnPy3(filename, text, name);
};
// +++++++++++++++++//
/// USEFUL FUNCTIONS/////
// +++++++++++++++++//
var writeJSON = (data, place) => {
	if (data == undefined || data == null || data == '') {
		console.log('NOT DB_updated b/o data is undefined');
		return;
	} else {
		fs.writeFile(place, JSON.stringify(data, null, '    '));
		console.log('DB_updated at ' + place);
	};
};

// 日付をYYYY/MM/DD HH:DD:MI:SS形式で取得
var nowTime = () => {
	var date = new Date();
	var yyyy = date.getUTCFullYear();
	var mm = ("0" + date.getUTCMonth()).slice(-2);
	var dd = ("0" + date.getUTCDate()).slice(-2);
	var hh = ("0" + date.getUTCHours()).slice(-2);
	var mi = ("0" + date.getUTCMinutes()).slice(-2);
	var ss = ("0" + date.getUTCSeconds()).slice(-2);
	return (yyyy + mm + dd + hh + mi + ss);
};

var split2List = (s, form = ',') => {
	if (~s.indexOf(form)) {
		var sList = s.split(form);
	} else {
		sList = [s];
	}
	return sList;
};

var cutMin = (list, Num = 3) => {
	var lenList = list.length - 1;
	if (lenList != -1) {
		do {
			var str = list[lenList];
			if (str.length < Num) {
				list[lenList] = '';
			}
		} while (lenList--);
		// filter関数で空白を削除
		list = list.filter((e) => { return e !== ""; });
		return list;
	}
	else return;
}

var hira2kana = function(str, opt = true) {
	str = str
		.replace(/[ぁ-ゔ]/g, function(s) {
			return String.fromCharCode(s.charCodeAt(0) + 0x60);
		})
		.replace(/ﾞ/g, '゛')
		.replace(/ﾟ/g, '゜')
		.replace(/(ウ゛)/g, 'ヴ')
		.replace(/(ワ゛)/g, 'ヷ')
		.replace(/(ヰ゛)/g, 'ヸ')
		.replace(/(ヱ゛)/g, 'ヹ')
		.replace(/(ヲ゛)/g, 'ヺ')
		.replace(/(ゝ゛)/g, 'ヾ')
		.replace(/ゝ/g, 'ヽ')
		.replace(/ゞ/g, 'ヾ');
	if (opt !== false) {
		str = str.replace(/ゕ/g, 'ヵ').replace(/ゖ/g, 'ヶ');
	}
	return str;
};
var kana2hira = function(str,opt) {
	str = str
		.replace(/[ァ-ヴ]/g, function(s) {
			return String.fromCharCode(s.charCodeAt(0) - 0x60);
		})
		.replace(/ﾞ/g, '゛')
		.replace(/ﾟ/g, '゜')
		.replace(/(う゛)/g, 'ゔ')
		.replace(/ヷ/g, 'わ゛')
		.replace(/ヸ/g, 'ゐ゛')
		.replace(/ヹ/g, 'ゑ゛')
		.replace(/ヺ/g, 'を゛')
		.replace(/(ヽ゛)/g, 'ゞ')
		.replace(/ヽ/g, 'ゝ')
		.replace(/ヾ/g, 'ゞ');
	if (opt !== false) {
		str = str.replace(/ヵ/g, 'ゕ').replace(/ヶ/g, 'ゖ');
	}
	return str;
};
var zenkana2hankana = function(str) {
	var kanaMap = {
		'ガ': 'ｶﾞ', 'ギ': 'ｷﾞ', 'グ': 'ｸﾞ', 'ゲ': 'ｹﾞ', 'ゴ': 'ｺﾞ',
		'ザ': 'ｻﾞ', 'ジ': 'ｼﾞ', 'ズ': 'ｽﾞ', 'ゼ': 'ｾﾞ', 'ゾ': 'ｿﾞ',
		'ダ': 'ﾀﾞ', 'ヂ': 'ﾁﾞ', 'ヅ': 'ﾂﾞ', 'デ': 'ﾃﾞ', 'ド': 'ﾄﾞ',
		'バ': 'ﾊﾞ', 'ビ': 'ﾋﾞ', 'ブ': 'ﾌﾞ', 'ベ': 'ﾍﾞ', 'ボ': 'ﾎﾞ',
		'パ': 'ﾊﾟ', 'ピ': 'ﾋﾟ', 'プ': 'ﾌﾟ', 'ペ': 'ﾍﾟ', 'ポ': 'ﾎﾟ',
		'ヴ': 'ｳﾞ', 'ヷ': 'ﾜﾞ', 'ヺ': 'ｦﾞ',
		'ア': 'ｱ', 'イ': 'ｲ', 'ウ': 'ｳ', 'エ': 'ｴ', 'オ': 'ｵ',
		'カ': 'ｶ', 'キ': 'ｷ', 'ク': 'ｸ', 'ケ': 'ｹ', 'コ': 'ｺ',
		'サ': 'ｻ', 'シ': 'ｼ', 'ス': 'ｽ', 'セ': 'ｾ', 'ソ': 'ｿ',
		'タ': 'ﾀ', 'チ': 'ﾁ', 'ツ': 'ﾂ', 'テ': 'ﾃ', 'ト': 'ﾄ',
		'ナ': 'ﾅ', 'ニ': 'ﾆ', 'ヌ': 'ﾇ', 'ネ': 'ﾈ', 'ノ': 'ﾉ',
		'ハ': 'ﾊ', 'ヒ': 'ﾋ', 'フ': 'ﾌ', 'ヘ': 'ﾍ', 'ホ': 'ﾎ',
		'マ': 'ﾏ', 'ミ': 'ﾐ', 'ム': 'ﾑ', 'メ': 'ﾒ', 'モ': 'ﾓ',
		'ヤ': 'ﾔ', 'ユ': 'ﾕ', 'ヨ': 'ﾖ',
		'ラ': 'ﾗ', 'リ': 'ﾘ', 'ル': 'ﾙ', 'レ': 'ﾚ', 'ロ': 'ﾛ',
		'ワ': 'ﾜ', 'ヲ': 'ｦ', 'ン': 'ﾝ',
		'ァ': 'ｧ', 'ィ': 'ｨ', 'ゥ': 'ｩ', 'ェ': 'ｪ', 'ォ': 'ｫ',
		'ッ': 'ｯ', 'ャ': 'ｬ', 'ュ': 'ｭ', 'ョ': 'ｮ',
		'。': '｡', '、': '､', 'ー': 'ｰ', '「': '｢', '」': '｣', '・': '･','？':'?','！':'!'
	};
	var reg = new RegExp('(' + Object.keys(kanaMap).join('|') + ')', 'g');
	return str
		.replace(reg, function(match) {
			return kanaMap[match];
		})
		.replace(/ﾞ/g, '゛')
		.replace(/ﾟ/g, '゜');
};
var getKaomoji = (str) => {
	var text = '[0-9A-Za-zぁ-ヶ一-龠]';
	var non_text = '[^0-9A-Za-zぁ-ヶ一-龠]';
	var allow_text = '[ovっつ゜ニノ三二]';
	var hw_kana = '[ｦ-ﾟ]';
	var open_branket = '[\(∩꒰（]';
	var close_branket = '[\)∩꒱）]';
	var arround_face = '(?:' + non_text + '|' + allow_text + ')*';
	var face = '(?!(?:' + text + '|' + hw_kana + '){3,}).{3,}';
	var face_char = new RegExp(arround_face + open_branket + face + close_branket + arround_face);
	var kaomoji = str.match(face_char);
	// console.log(kaomoji)
	return kaomoji;
}
// +++++++++++++++++//
/// Thenable MODULEs /////
// +++++++++++++++++//
var getMA = (s: string, form: string = 'all', mode: string = 'default', exp: string = 'standard') => {
	return new Promise((resolve, reject) => { 
		s = s.replace("\u3000", '').replace("\t", '').replace('\n', '');
		var kaomoji = getKaomoji(s);
		// console.log(kaomoji)
		if(kaomoji != null){
			var kao = kaomoji[0];
			s = s.replace(kao,'( ^ω^ )')
		};
		var ans = mecab.parse(s, (err, result) => {
			if (err) { reject(err); }
			if(kaomoji != null){
				result = _.map(result, (info) => {
					if(info[0] != '( ^ω^ )'){
						return info
					} else {
						return [kao, '記号', '顔文字',  '*', '*', '*', '*', kao , 'エガオ', 'エガオ']
					};
				};
				resolve(result);
			} else {
				resolve(result);
			};
		});

	}).catch((e) => {
		console.log(e);
	}).then((result) => {
		switch(form){
			case 'all':
				return Promise.resolve(result);
				break;
			case 'standard':
				form = '名詞,動詞,形容詞,副詞,助詞,助動詞,接頭詞,感嘆詞,感動詞';
				break;
			default:
				break;
		};

		return Promise.all(_.map(result, (adata) => {
			var formls = split2List(form);
			return Promise.all(_.map(formls, (aform) => {
				if (adata[1] == aform) {
					return Promise.resolve(adata);
				};
			})).then((adata) => {
				adata = _.compact(adata);
				return Promise.resolve(adata[0]);
			}).catch((e) => {
				console.log(e);
			});
		})).then((r) => {
			r = _.compact(r);
			return Promise.resolve(r);
		}).catch((e) => {
			console.log(e);
		});
	}).then((result) => {
		switch (exp) {
			case 'none':
				return Promise.resolve(result);
				break;
			case 'standard':
				exp = "数,人名,接尾,非自立,接続助詞,格助詞,代名詞";
				break;
			default:
				break;
		};
		var arrExp = split2List(exp);
		return Promise.all(_.map(result, (word) => {
			var boolExplist = _.map(arrExp, (Exp) => {
				if (Exp == word[2]) {
					return true;
				} else {
					return false;
				};
			});
			var isExp: boolean = _.contains(boolExplist, true);
			if (isExp == false) {
				return Promise.resolve(word);
			};
		}));
	}).then((result) => {
		result = _.compact(result);
		mode = mode.replace(/原形/, 'g').replace(/カタカナ/, 'k').replace(/詳細/, 'detail').replace(/リスト/, 'n');
		switch (mode) {
			case 'n':
				return Promise.all(_.map(result, (word) => {
					return Promise.resolve(word[0]);
				})); break;
			case 'g':
				return Promise.all(_.map(result, (word) => {
					if (word[7] != '*') {
						return Promise.resolve(word[7]);
					} else {
						return Promise.resolve(word[0]);
					};
				})); break;
			case 'k':
				return Promise.all(_.map(result, (word) => {
					if (word[8] != undefined) {
						return Promise.resolve(word[8]);
					} else {
						return Promise.resolve(word[0]);
					};
				})); break;
			default:
				return Promise.resolve(result);
				break;
		};
	}).catch((e) => {
		console.log(e);
	});
};
var sensitiveCheck = (q) => {
	return new Promise((resolve, reject) => {
		var client = this;
		var postURL = 'https://api.apigw.smt.docomo.ne.jp/truetext/v1/sensitivecheck?APIKEY=' + DAPIKEY;
		request.post({
			uri: postURL,
			form: 'text=' + encodeURIComponent(q) + '&extflg=1',
			json: true
		}, (error, response, body) => {
			if(response.statusCode != undefined){
				if (response.statusCode == 200) {
					client.context = body.context;
				};
			} else {
				error = new Error(body);
				reject(error);
			};
			resolve(body);
		});
	}).catch((error) => {
		console.log(error + '[sensitiveCheck]');
		return Promise.resolve('OK');
	});
};



var any2hankana = (s) => {
	var kana = hira2kana(s)
	return getMA(kana, 'all', 'k', '').then((result) => {
		return result.join('');
	}).then((zenkana) => {
		return zenkana2hankana(zenkana);
	});
};

var createDialogue = (utt, info, character = 'U') => {
	switch(character){
		default:
			var char = 0; break;
		case 'R':
			var char = 0; break;
		case 'N':
			var char = 20; break;
	};
	var client = this;
	return Promise.resolve().then(() => {
		if (info.context == ''){
			var context = client.this;
		} else {
			context = info.context;
		};
		var postURL = 'https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue?APIKEY=' + DAPIKEY;
		var param = {
				uri: postURL,
				method: 'POST',
				json: {
				  "utt": utt,
				  "context": context,
				  "mode": "dialog",
				  "t": char
				}
			};
		return Promise.resolve(param);
	}).then((param) => {
		return new Promise((resolve, reject) => {
			request(param, (error, response) => {
				if (!error && response.statusCode == 200) {
					resolve(response.body);
				} else {
					reject(response);
				};
			});
		});
	}).then((result) => {
		info.context = result.context;
		return Promise.resolve([result, info]);
	}).catch((error) => {
		return Promise.reject(error.statusCode + '[createDialogue]');
	});
};

var clusterAnalysis = (q) => {
	return new Promise((resolve, reject) => {
		var client = this;
		var postURL = 'https://api.apigw.smt.docomo.ne.jp/truetext/v1/clusteranalytics?APIKEY=' + DAPIKEY;
		request.post({
			uri: postURL,
			form: 'text=' + encodeURIComponent(q) + '&extflg=0',
			json: true
		}, (error, response, body) => {
			if (!error && response.statusCode != undefined) {
				if (response.statusCode == 200) {
					client.context = body.context;
				};
			} else {
				error = new Error(body);
				reject(error);
			};
			resolve(body);
		});
	}).catch((error) => {
		console.log(error + '[clusterAnalysis]');
		return Promise.resolve('OK');
	});
};


var sensitiveCheck = (q) => {
	return new Promise((resolve, reject) => {
		var client = this;
		var postURL = 'https://api.apigw.smt.docomo.ne.jp/truetext/v1/sensitivecheck?APIKEY=' + DAPIKEY;
		request.post({
			uri: postURL,
			form: 'text=' + encodeURIComponent(q) + '&extflg=1',
			json: true
		}, (error, response, body) => {
			if(response.statusCode != undefined){
				if (response.statusCode == 200) {
					client.context = body.context;
				};
			} else {
				error = new Error(body);
				reject(error);
			};
			resolve(body);
		});
	}).catch((error) => {
		console.log(error + '[sensitiveCheck]');
		return Promise.resolve('OK');
	});
};

var sensitiveCheckU = (utt) => {
	return sensitiveCheck(utt).then((body) => {
		if (body.status == 'OK') {
			return Promise.resolve('OK');
		} else {
			return Promise.resolve(body.quotients);
		};
	}).then((quo) => {
		var quo0 = quo[0];
		var cluster = quo0.cluster_name;
		var dngRate = quo0.quotient_rate;
		var dngID = quo0.quotient_id;
		var ans = 'OK';
		if (dngID != undefined) {
			switch (dngID) {
				default:
					ans = 'unknown' + dngID;
					return Promise.resolve(ans); break;
				case 'arg': //隠語
					if (cluster = '2ちゃんねる用語') {
						ans = 'OK';
					} else { ans = '隠語はいっぱいあって、私には難しいです...'; }
					return Promise.resolve(ans); break;
				case dngID = 'ins': //ネットスラング
					ans = 'ネットスラングですか...';
					return Promise.resolve(ans); break;
				case dngID = 'ppm': //心理現象
					ans = '心理現象を理解するのは、私には難しいです...';
					return Promise.resolve(ans); break;
				case dngID = 'gmb': //賭け事
					ans = '賭け事なんてしちゃいけないって教わってきましたから...';
					return Promise.resolve(ans); break;
				case dngID = 'adt'://アダルト
					if (cluster == '生殖器スラング') {
						ans = '全く、小中学生じゃないんですから..そんなこといって喜ばないでください(怒) ハレンチですっ!!';
					} else if (cluster == '性行為・性的嗜好') {
						ans = '人にはそれぞれ嗜好があるとは思いますけれど..ハレンチですっ ///';
					} else ans = 'ハレンチですっ!!';
					return Promise.resolve(ans); break;
				case dngID = 'hms': //同性愛
					var hmsList = ['ホモはNG', 'ホモは帰って、どうぞ。'];
					ans = _.sample(hmsList);
					return Promise.resolve(ans); break;
				case dngID = 'brt': //風俗
					ans = '風俗のお話はお断りです。';
					return Promise.resolve(ans); break;
				case dngID = 'ifg': //利権侵害
					ans = '利権侵害...!!';
					return Promise.resolve(ans); break;
				case dngID = 'stk': //ストーカー
					ans = 'あなたは、ストーカーですか? 気持ち悪いです。';
					return Promise.resolve(ans); break;
				case dngID = 'cym': //サイバー犯罪
					ans = 'サイバー犯罪はいけませんよ？';
					return Promise.resolve(ans); break;
				case dngID = 'acd': //事故
					ans = '事故関連のお話は、ちょっと...';
					return Promise.resolve(ans); break;
				case dngID = 'scd': //自殺
					ans = '私は、人生を全うしたいです。';
					return Promise.resolve(ans); break;
				case dngID = 'mrd': //殺人
					ans = '人の命を奪う重大さを考えてください、ね。';
					return Promise.resolve(ans); break;
				case dngID = 'crm': //事件・犯罪
					if (cluster == 'テロ・テロ組織') {
						ans = 'テロってそのうち日本でも頻繁に起きるようになるんしょうか。怖いです...';
					} else {
						ans = '穏やかじゃないですね...';
					}
					return Promise.resolve(ans); break;
				case dngID = 'rlg': //'カルト教団・カルト宗教'
					if (cluster == 'カルト教団・カルト宗教') {
						ans = 'カルト宗教、怖いです...とりあえず、宗教の話はNGでお願いします。';
					} else if (cluster == '宗教・宗教団体') {
						ans = '「スピリチュアルパワー注入♪」って言ってる痛い人いた気がしますね。';
					} ans = '宗教を理解するのは難しいです...';
					return Promise.resolve(ans); break;
				case dngID = 'plt': //政治
					if (cluster = '内閣') {
						ans = 'OK';
					} else if (cluster = '日本史') {
						ans = 'OK';
					} else if (cluster = '世界史') {
						ans = 'OK';
					} else ans = '政治の話ですか? 確かに18歳選挙も始まりますししっかりと考えなくてはなりませんね...';
					return Promise.resolve(ans); break;
				case dngID = 'drg'://薬物
					ans = 'クスリは身を滅ぼしますよ?';
					return Promise.resolve(ans); break;
				case dngID = 'war'://戦争・テロ
					var bukiList = ['武器にはいろんな種類があって難しいですね。', 'パイソンいいですよね。', 'ちなみにこのAIはpythonで書かれているんです...って違いますね。'];
					var soubiList = ['最近そういうアニメとかゲームが増えてきましたね。', 'やっぱり、大艦巨砲主義ですよ。', 'ロマンですね。'];
					if (cluster == '武器') {
						ans = _.sample(bukiList);
					} else if (cluster == '軍事技術・軍需産業') {
						ans = '装備品について私も勉強中ですっ♪。';
						ans = _.sample(soubiList);
					} else ans = 'もう少し、平和なお話にしませんか?';
					return Promise.resolve(ans); break;
				case dngID = 'dtg'://出会い系
					ans = '出会い系だなんて...ハレンチです...';
					return Promise.resolve(ans); break;
				case dngID = 'dsc'://差別
					ans = '差別表現は、国によっては違法ですよ?';
					return Promise.resolve(ans); break;
				case dngID = 'dng'://危険
					ans = '危ないですから、やめてください...';
					return Promise.resolve(ans); break;
				case dngID = 'frd'://詐欺・偽装
					ans = '私をだまそうとしても無駄ですよ?詐欺や偽装にはひっかかりませんっ!!';
					return Promise.resolve(ans); break;
				case dngID = 'gns'://暴力団
					ans = '私たちには、そちら側のルールがわからないです...';
					return Promise.resolve(ans); break;
				case dngID = 'aus'://暴力・虐待
					ans = '暴力に訴えるなんて、卑怯です...';
					return Promise.resolve(ans); break;
				case dngID = 'bml'://闇金融
					ans = '闇金融には関わりたくないです...';
					return Promise.resolve(ans); break;
				case dngID = 'smg'://密輸
					ans = '私には、密輸なんてできません...';
					return Promise.resolve(ans); break;
			};
		} else return Promise.resolve(ans);
	}).catch((error) => {
		console.log(error + '[sensitiveCheckU]');
		var ans = 'OK';
		return Promise.resolve(ans);
	});
};
var searchWiki = (q) => {
	return new Promise((resolve, reject) => {
		var getURL = 'http://wikipedia.simpleapi.net/api?keyword=' + encodeURIComponent(q) + '&output=json';
		request(getURL, (error, response, body) => {
			var body = JSON.parse(body);
			if (response.statusCode !== 200) {
				error = new Error(body);
			} else {
				console.log(body)
				resolve(body);
			};
		});
	}).then((result) => {
		return Promise.resolve(result[0].body.split('<br/>')[0].split('である。')[0];
	}).catch((e) => {
		return Promise.resolve('検索しましたが、見つかりませんでした。');
	});
};

var QA = (q) => {
	return new Promise((resolve, reject) => {
		var getURL = 'https://api.apigw.smt.docomo.ne.jp/knowledgeQA/v1/ask?APIKEY=' + DAPIKEY + '&q=' + encodeURIComponent(q);
		request(getURL, (error, response, body) => {
			var body = JSON.parse(body);
			if (response.statusCode !== 200) {
				error = new Error(body);
			};
			resolve(body);
		});
	});
};
var understand = (utt) => {
	return new Promise((resolve, reject) => {
		var client = this;
		var postURL = 'https://api.apigw.smt.docomo.ne.jp/sentenceUnderstanding/v1/task?APIKEY=' + DAPIKEY;
		var language = 'ja';
		var params = {
			"projectKey": "OSU", //固定
			"appInfo": {
				"appName": "_umiA",
				"appKey": "_umiA ver5.43"
			},
			"clientVer": "1.0.0",
			"language": language,
			"userUtterance": {
				"utteranceText": utt
			}
		};
		request({
			uri: postURL,
			method: 'POST',
			json: params
		}, (error, response, body) => {
			if (!error && response.statusCode == 200) {
				client.context = body.context;
			} else {
				error = new Error(body);
			};
			resolve(body);
		});
	});
};

var YahooKey = (q) => {
	return new Promise((resolve, reject) => {
		var getURL = 'http://jlp.yahooapis.jp/KeyphraseService/V1/extract?appid=' + YAPIKEY + '&sentence=' + encodeURIComponent(q) + '&output=json';
		request(getURL, (error, response, body) => {
			var body = JSON.parse(body);
			if (response.statusCode !== 200) {
				error = new Error(body);
			};
			resolve(body);
		});
	});
};

var eStatSearch = (q, limitcnt:number = 10) => {
	return new Promise((resolve, reject) => {
		var getURL = 'http://api.e-stat.go.jp/rest/2.0/app/json/getStatsList?appId=' + eStat_API_ID + '&lang=J&searchKind=1&limit=' + limitcnt + '&searchWord=' + encodeURIComponent(q);
		request(getURL, function(error, response, body) {
			var body = JSON.parse(body);
			resolve(body['GET_STATS_LIST']);
		});
	}).catch((e) => {
		console.log(e);
	});
};

var eStatgetData = (statsID, limit =10000) => {
	return new Promise((resolve, reject) => {
		var getURL = 'http://api.e-stat.go.jp/rest/2.0/app/json/getStatsData?appId=' + eStat_API_ID + '&lang=J&statsDataId=' + statsID;
		request(getURL, function(error, response, body) {
			var body = JSON.parse(body);
			console.log(body);
			resolve(body['GET_STATS_DATA']);
		});
	}).catch((e) => {
		console.log(e);
	});
};
var nazukiSA = (q, KEY = DAPIKEY) => {
	return new Promise((resolve, reject) => {
		var client = this;
		var postURL = 'https://api.apigw.smt.docomo.ne.jp/nazukiSA/v1/analyze?APIKEY=' + KEY;
		request({
			uri: postURL,
			method: 'POST',
			json: {
				"option": "SP+K+N+X",
				"text": q
			}
		}, (error, response) => {
			if(error){
				error = new Error(response);
				reject(error);
			} else {
				resolve(response.body);
			};
		});
	}).then((body) => {
		console.log(body)
		var returncode = body['return-code'];
		if(returncode == 0){
			var ret = body['page-results'][0]['sentence-results'][0];
			return Promise.resolve(ret);
		} else if(returncode == 1002){ 
			return Promise.reject('日本語でない。')
		} else if(body['requestError']['policyException']['messageId'] == 'POLSLA002'){
			console.log('[ERR][nazukiSA.POLSLA002]change_ID');
			return nazukiSA(q, DAPIKEY);
		} else {
			return Promise.reject(returncode); 
		};
	}).catch((error) => {
		console.log(error + '[nazukiSA]');
		return Promise.resolve('OK');
	});
};
var nazukiSA_Main = (text) => {
	return nazukiSA(text).then((result) => {
		// console.log(result)
		var nazukiintx = Dics.nazukiSA.intx;
		var nazukitabx = Dics.nazukiSA.tabx;
		var intxPromisify = new Promise((resolve, reject) => {
				resolve(_.map(result['intx-results'], (intx) => {
					var relations = _.map(intx['relations'], (r) => { return r["surface"]; });
					var senseName = intx['sense-id'];
					return [nazukiintx[senseName], relations];
				}));
			});
		var kexPromisify = new Promise((resolve, reject) => {
				resolve(_.map(result['kex-results'], (kex) => {
					var keyword = kex["surface"];
					var keyscore = kex['score'];
					return [keyword, keyscore];
				}));
			});
		var tabxPromisify = new Promise((resolve, reject) => {
				resolve(_.map(result['type2-results'], (tabx) => {
					var tabooRSN = tabx["reason-id"];
					var tabooScore = tabx['score'];
					var tabooWords = _.map(tabx['instances'], (instance, index, array) {
						return instance['surface'];
					};
					return [nazukitabx[tabooRSN], tabooScore, tabooWords];
				}));
			});
	return Promise.all([intxPromisify, kexPromisify, tabxPromisify])
		.then((result) => {
			var intx = result[0];
			var kex = result[1];
			var tabx = result[2];
			var sense = ['他','無','無'];
			var intxTG = '';
			if (intx[0] != undefined) {
				var intx0 = intx[0];
				sense = intx0[0];
				intxTG = intx0[1];
			};
			if (kex[0] == undefined) {
				kex = [['', 1]]
			};
			if (tabx[0] == undefined) {
				tabx = [['']]
			};

			return Promise.resolve({
				"intx": sense,
				"intxTG": intxTG,
				"kex" : kex,
				"tabx" : tabx
			});
		});
	}).catch((e) => {
		console.log(e, 'at [nazukiSA]');
		return Promise.resolve({
				"intx": ['','',''],
				"intxTG": '',
				"kex" : [['', 1]],
				"tabx" : [['']]
			});
	});
};

var plagiarize = () =>{
	return getSQLTweet({id : Math.floor(Math.random()*1000)})
	.then((tweet) => {
		var text = tweet['text'];
		if (_.include(text, 'RT')){
			return Promise.reject('excludeRT');
		};
			var sList = text.replace('？','。').split('。')
			return textFilter(sList[0]).then((result) => 
				return Umichar2(result)
				.then((r)=>{
					return Promise.resolve(r);
				}).catch((e) =>{
					return Promise.reject(e);
				});
			});
		}).then((r) => {
			return Promise.resolve(r);
		}).catch((e) =>{
			return Promise.resolve('');
		});
	});
};

var answerDAPI = (s, info) => {
	var character = 'U';
	var char = 0;
	var ans;
	var name = info.screen_name;
	return Promise.resolve().then((arg) => {
			var sense = '無';
			var tabooRSN = '';
			if (tabooRSN != ''){
				return getPhrase({character: character, s_type: tabooRSN+'注意'})
				.then((result) => {
					// console.log(result)
					ans = result.phrase;
					return Promise.resolve([ans, info]);
				}).catch((e) => {
					console.log('dialog_absorption')
					return createDialogue(s, info).then((arg) => {
						var result = arg[0];
						var altinfo = arg[1];
						return Promise.resolve([result.utt, altinfo]);
					});
				});
			} else {
				switch (sense) {
					default:
					var rnd = Math.random();
					// console.log(rnd)
               if (rnd < 0.2) {
						return plagiarize().then((result) => {
							// console.log(result)
							// if(result.phrase == undefined){return Promise.reject('dialog');}
							if(result == ''){return Promise.reject('rt');}
							ans = result + '\n(β)';
							return Promise.resolve([ans, info]);
						}).catch((e) => {

						});
					} else {
						return createDialogue(s, info).then((arg) => {
							var result = arg[0];
							var altinfo = arg[1];
							return Promise.resolve([result.utt, altinfo]);
						});
                }; break;
					case '問い合わせ':
						return QA(s).then((data) => {
							// console.log(data);
							if (data == undefined) {
								ans = 'わかりませんでした...';
								return Promise.resolve([ans, info]);
							} else {
								// console.log(data);
								var qaanswers = data.answers
								var qaanswer = qaanswers[0];
								if (qaanswer == undefined) {
									// console.log(qaanswer);
									ans = '調べましたが、' + data.message.textForDisplay;
									return Promise.resolve([ans, info]);
								} else {
									ans = qaanswer.answerText;
									if (ans != undefined) {
										var qaanswer1 = qaanswers[1];
										if(qaanswer1 != undefined){
											ans = 'おそらく' + ans + '…だと思いますよ？' + data.answers.length + 'つの候補がありました。もしかすると、' + qaanswer1.answerText + 'かも...';
										} else {
											ans = 'きっと' + ans + '…だと思いますよ？';
										};
										return Promise.resolve([ans, info]);
									};
								};
							};
						});
						break;
				};					
			// };
		// });
	}).catch((error) => {
		console.log(error);
		return getPhrase({character: character, s_type: 'error'}).then((result) => {
			ans = result.phrase;
			return Promise.resolve([ans, info]);
		});
	});
};

// +++++++++++++++++//
/// Thenable MODULEs /////
// +++++++++++++++++//
var tweet = (text, char: string = '', screen_name = '', status_id = '', cntRetry = 0, delay = 0) => {
	var mode = 'tweet' + char;
	var twtr;
	switch (char) {
		case 'U':
			twtr = twtrU; break;
		case 'R':
			twtr = twtrR; break;
		default:
			console.log('[tweet_demo] ' + text); return; break;
	};
	var ans = '';
	var ans2 = '';
	return new Promise((resolve, reject) => {
		if (screen_name != '') {
			var tweet = '@' + screen_name + ' ' + text;
		} else {
			tweet = text;
		};
		if (tweet.length > 140) {
			if (screen_name != '') {
				var anstext = '@' + screen_name + ' ' + text;
				ans = anstext.slice(0, 137) + '...';
				ans2 = '@' + screen_name + ' ' + '...' + anstext.slice(137, 250);
			} else {
				ans = text.slice(0, 137) + '...';
				ans2 = '...' + text.slice(137, 275);
			};
			tweet = ans
		};
		var tweetJson;
		if (status_id != '') {
			tweetJson = { status: tweet, in_reply_to_status_id: status_id };
		} else {
			tweetJson = { status: tweet };
		};
		if (tweetJson != undefined) {
			twtr.post('statuses/update', tweetJson, (error, tweet, response) => {
				if (error) {
					reject(error);
				} else {
					cntRetry = 0;
					console.log(tweet.text);
					resolve(tweet);  // Tweet body. 
				};
			});
		};
	}).then((tweet) => {
		if (ans2 != '') {
			var tweetJson = { status: ans2, in_reply_to_status_id: tweet['id_str'] };
			if (tweetJson != undefined) {
				twtr.post('statuses/update', tweetJson, (error, tweet, response) => {
					if (error) {
						console.log(error);
					} else {
						cntRetry = 0;
						console.log(tweet.text);
						return Promise.resolve(tweet)  // Tweet body. 
					};
				});
			};
		} else {
			return Promise.resolve(tweet);
		};
	}).catch((e) => {
			return reconAlgo(cntRetry, delay, mode, e)
				.then((arg) => {
					cntRetry = arg[0];
					delay = arg[1];
					setTimeout(() => {
						return tweet(text, char, screen_name, status_id, cntRetry, delay);
					}, delay);
				}).catch((e) => {
					// if (e == 'Over daily update') {
						// text = 'ツイート規制されました。DMに転送しています。\n' + text;
						return;
					// };
				});
	});
};

var dm = (dm, char = 'U', screen_name = 'xxxx', cntRetry = 0, delay = 0, limit = 10000) => {
	return new Promise((resolve, reject) => {
		var twtr;
		switch(char){
			case 'U':
				twtr = twtrU; break;
			case 'R':
				twtr = twtrR; break;
			default:
				console.log('[dm_demo]' + dm); return; break;
		};
		twtr.post('direct_messages/new', { text: dm, screen_name: screen_name }, (error, dm, response) => {
			if (error) {
				reject(error);
			} else {
				cntRetry = 0;
				console.log(dm.text);
				resolve(dm);  // Tweet body. 
			};
		});
	}).catch((e)=>{
		var mode = 'dm' + char;
		return reconAlgo(cntRetry, delay, mode, e)
		.then((arg) => {
			cntRetry = arg[0];
			delay = arg[1];
			setTimeout(() => {
				return dm(dm, screen_name, char, cntRetry, delay);
			}, delay);
		}).catch((e)=>{
			console.log(e);
		});
	});
};
var quote = (comment:string, char:string, screen_name: string, status_id: string) => {
	var mode = 'quote' + char;
	var quotetext = comment + "https://twitter.com/" + screen_name + "/status/" + status_id;
	return tweet(quotetext, char);
};

var follow = (char = 'U', screen_name = 'xxxx', cntRetry = 0, delay = 0, limit = 10000) => {
	return new Promise((resolve, reject) => {
		var twtr;
		switch (char) {
			case 'U':
				twtr = twtrU; break;
			case 'R':
				twtr = twtrR; break;
			default:
				twtr = twtrE; break;
		};
		twtr.post('friendships/create', { screen_name: screen_name }, (error, response) => {
			if (error) {
				reject(error);
			} else {
				cntRetry = 0;
				console.log(response);
				resolve(response);  // Tweet body. 
			};
		});
	}).catch((e) => {
		var mode = 'follow' + char;
		return reconAlgo(cntRetry, delay, mode, e)
			.then((arg) => {
				cntRetry = arg[0];
				delay = arg[1];
				setTimeout(() => {
					return follow(char, screen_name, cntRetry, delay);
				}, delay);
			}).catch((e) => {
				console.log(e);
			});
	});
};
// var tweetId = 'XXXXX';
// client.post('statuses/retweet/' + tweetId, function(error, tweet, response) {
// 	if (!error) {
// 		console.log(tweet);
// 	}
// });

var reconAlgo = (cntRetry, delay, mode = 'Func', error = 'error') => {
	return new Promise((resolve, reject) => {
		cntRetry++;
		if (cntRetry == 1) { console.error(error); };
		var error0 = error[0];
		var errorcode = error0['code'];
		switch(errorcode){
			case 185:
				reject('Over daily update');
				break;
			case 186:
				reject('over140chars');
			case 187:
				reject('Status is a duplicate.');
				break;
			case 226:
				reject('as spam');
				break;
			default:
				if (delay < 16000) {
					delay = 250 * cntRetry;
					console.error('[' + mode + '] TCP/IPレベルエラー 線形的に再接続しています... 試行回数: ' + cntRetry + ' 次回接続まで' + delay + 'ミリ秒');
				} else if (delay < 240000) {
					delay = delay * 2;
					console.error('[' + mode + '] HTTPレベルエラー 指数関数方式で再接続しています... 試行回数: ' + cntRetry + ' 次回接続まで' + delay + 'ミリ秒');
				} else if (cntRetry < 100) {
					console.error('[' + mode + '] エラー 固定秒数で再接続しています... 試行回数: ' + cntRetry + ' 次回接続まで' + delay + 'ミリ秒');
				} else {
					reject('reconnect Algorithm Finished: Failed to reconnect...');
				};
		};
		resolve([cntRetry, delay]);
	});
};


var getDM = (count = 5, cntRetry = 0, delay = 250) => {
	return new Promise((resolve, reject) => {
		cntRetry = 0;
		var mode = 'getDM';
		twtrU.get('direct_messages', { count: count }, (error, data, response) => {
			if (error) {
				reject(error);
			} else {
				resolve(data);
			};
		});
	}).catch((e) => {
		cntRetry++;
		var mode = 'getDM';
		return reconAlgo(cntRetry, delay, mode, e)
			.then((arg) => {
				cntRetry = arg[0];
				delay = arg[1];
				setTimeout(() => {
					return getDM(count, cntRetry, delay);
				}, delay);
			}).catch((e) => {
				console.log(e);
			});
	});
};
var getMTLp = (count = 5, cntRetry = 0, delay = 250, since_id = 1) => {
	//Promise Base で　get Mention Timeline.
	return new Promise((resolve, reject) => {
		var mode = 'getMTL';
		twtrU.get('statuses/mentions_timeline', { count: count, since_id: since_id, include_entities: true }, (error, tweet, response) => {
			if (error) {
				reject(error);
			} else {
				resolve(tweet);
			};
		});
	}).then((data) => {
		if (data == undefined) {
			return Promise.reject(data);
		} else {
			return Promise.resolve(data);
		};
	}).catch((e) => {
		cntRetry++;
		var mode = 'getMTLp';
		return reconAlgo(cntRetry, delay, mode, e)
			.then((arg) => {
				cntRetry = arg[0];
				delay = arg[1];
				setTimeout(() => {
					return getMTLp(count, cntRetry, delay, since_id);
				}, delay);
			}).catch((e) => {
				console.log(e);
			});
	});
};

// var tags = []
var Main = (text, screen_name = 'xxxx', char = '', output = '', data = '', Debug = false) => {
	var cmd = '';
	var tags = [];
	var BOT_ID;
	var BOT_NAME;
	var startTime = new Date();
	switch (char) {
		case 'U':
			BOT_ID = '2805015776'; //メイン @_umiA
			BOT_NAME = '_umiA';
			break;
		case 'R':
			BOT_ID = '538086375'; //規制回避bot @_rinM
			BOT_NAME = '_rinM';
		default:
			BOT_ID = '4333033044'; //実験bot @EEE
			BOT_NAME = '_evlP';

			// var BOT_ID = '2992260014'; //実験用bot @pEEE
	};
	return sequelize.transaction({
		// autocommit :false,
		isolationLevel: Sequelize.Transaction.READ_COMMITTED || "READ COMMITTED"
	}).then((trnU) => {
	// 	console.log(trn);
		var info = {};
		// ------------------------------------ 
		// ユーザーデータ読み込み部
		return User.findOne({ where: { screen_name: screen_name } }, {transaction: trnU})
		.then((userinfos) => {
			if(userinfos['dataValues'] == undefined || userinfos['dataValues'] == null){
				return Promise.reject('NodataValues')
			} else {
				var sql = userinfos['dataValues'];
				info = sql;
				// console.log(info);
				info['tags'] = ['__tags__'];
				info['status_id'] = data['id_str'];
				if((data['in_reply_to_status_id_str'] != null) || (data['in_reply_to_status_id_str'] !=undefined)){
					info['reply_id'] = null;
				} else {
					info['reply_id'] = data['in_reply_to_status_id_str'];
				};
				info['reply_name'] = data['in_reply_to_screen_name'];
				if (info['mode'] != 'verbal_learning') {
					info['lang'] = data['lang'];
				};
				if (info['lang'] == undefined || info['lang'] == 'und') { info['lang'] = 'ja' };
				if (info['langed'] == undefined || info['langed'] == 'und') { 
					info['langed'] = info['lang'];
				};
					info['tags'] = tags;
				if (data['entities'] != undefined){
					info['tags'] = _.map(data['entities']['hashtags'], 'text');
				};
				if (data['user'] != undefined) {
					var datauser = data['user'];
				} else if (data['sender'] != undefined) {
					var datauser = data['sender'];
				};
				if(datauser){
					info['name'] = datauser.name;
					info['usr_id'] = datauser.id_str;
					info['friends_cnt'] = datauser.friends_count;
					info['followers_cnt'] = datauser.followers_count;
					info['statuses_cnt'] = datauser.statuses_count;
					info['fav_cnt'] = datauser.favourites_count;
					if (info['exp'] = undefined || info['exp'] == 0) {
						info['exp'] = info['totalcnt'] * 100;
					};
				};
			};
			return Promise.resolve(info);
		}).catch((e) => {
			console.log(e);
			//newAccount
			info = 'newAccount';
			return Promise.resolve(info);
		}).then((info) => {
			// ------------------------------------ 
			// newAccount
			if (info == undefined || info == [] || info == 'newAccount') {
				console.log('[resolved]newAccount');
				return Promise.resolve(['newAccount', info]);
			};
			// ------------------------------------ 
			// 前回ツイートからの時間のズレを計測、保存
			var timedif = ~~nowTime() - ~~info.time;
			if (timedif < 0) { timedif = 0; };
			info.time = nowTime();
			console.log('前回接触から' + timedif + '秒経過');
			var cnt = info.cnt;
			// ------------------------------------ 
			// TAGs SELECTION
			tags = info.tags;
			// ------------------------------------ 
			// info.modeによるスイッチ
			var infomode = info.mode;
			return Promise.resolve().then(()=>{
				if (output == 'crawling') {
					return Promise.resolve(['Parrot', info]);
				};
				// ------------------------------------ 
				// WAITING & IGNORANCE
				switch (infomode) {
					case 'learn.q':
						info.cnt = 0;
						if (timedif > 180) { return Promise.resolve(['timeup', info]); };
						return Promise.resolve(['learn.q', info]);
						break;
					case 'waiting.eStat':
						info.cnt = 0;
						if (timedif > 180) { return Promise.resolve(['timeup', info]); };
						return Promise.resolve(['eStat.getTable', info]);
						break;
					case 'ignore.cnt':
						if (timedif < 900) {
							return Promise.resolve(['ignore', info]);
						};
						return Promise.resolve(['default', info]);
						break;
					case 'ignore.replycnt':
						if(info.recentID == info['reply_id']){
							console.log('[ignore.replycnt get the same id...]')
							return Promise.resolve(['ignore', info]);
						}else{
							return Promise.resolve(['default', info]);
						};
						break;
					case 'ignore.tooFreq':
						if (timedif < 100) {
							return Promise.resolve(['ignore', info]);
						} else {
							return Promise.resolve(['default', info]);
						};
						break;
					default:
						return Promise.resolve(['default', info]);
						break;
				};
			}).catch((e) => {
				console.log('[ERR][WAITING & IGNORANCE]');
				console.log(e);
				return Promise.resolve(['error', info]);
			}).then((arg) => {
				var mode = arg[0];
				var info = arg[1];
				if(mode != 'default'){
					return Promise.resolve([mode, info]);
				} else {
					// ------------------------------------ 
					// past REPLY LIMITATION
					// 遡ってのリプライは無視する。
					if (info.reply_id != undefined){
						var reply_id = info.reply_id;
					} else {
						// console.log(info);
						// console.log('[CATCH]reply_id undefined!!!!');
						reply_id = null;
					};
					var recent_id = info.recentID;
					var reply_name = info['reply_name'];
					// console.log(info);
					// info.auth = 'bot'
					if (reply_id != null) {
						if (reply_name != BOT_NAME){
							if (_.contains(info.auth, 'bot')){
								console.log('prevent_BOTinterrupt');
								return Promise.resolve(['ignore', info]);
							} else if (_.contains(info.auth, 'interruptRestriction')) {
								return Promise.resolve(['ignore', info]);
							} else {
								return Promise.resolve(['interrupt', info]);
							};
						} else {
							if (reply_id < recent_id) {
								return Promise.resolve(['ignore', info]);
							} else if (reply_id == recent_id) {
								info.replycnt++;
								return Promise.resolve(['default', info]);
							} else { 
								return Promise.resolve(['default', info]);
								// info.replycnt = info.replycnt - 1;
							};
						};
					} else {
						return Promise.resolve(['default', info]);
					};
				};
			}).catch((e) => {
				console.log('[ERR][REPLY LIMITATION]');
				console.log(e);
				return Promise.resolve(['error', info]);
			}).then((arg) => {
				// console.log(arg)
				var mode = arg[0];
				var info = arg[1];

				if(mode != 'default'){
					return Promise.resolve([mode, info]);
				} else {
					// ------------------------------------ 
					// MODE continue
					// var infomode = info.mode;
					switch (infomode) {
						case 'srtr':
							return Promise.resolve([infomode, info]);
							break;
						case 'twmon':
							return Promise.resolve([infomode, info]);
							break;
						case 'FAT':
							return Promise.resolve([infomode, info]);
							break;
						case 'replyFL':
							return Promise.resolve([infomode, info]);
							break;
						// case 'learn':
						// 	return Promise.resolve([infomode, info]);
						// 	break;
						// case 'dialogFL':
						// 	return Promise.resolve([infomode, info]);
						// 	break;
						default:
							var rnd = Math.random();
					// console.log(rnd)
							// ------------------------------------ 
							// INITIALIZE
							// 5分ごとに文脈とモードが初期化される。
							if (timedif > 300 || _.contains(tags, 'init') || _.contains(tags, '初期化')) {
								info.context = '';
								info.langed = info.lang;
								console.log(timedif + 'sec [Initializing...]');
								return Promise.resolve(['default', info]);
							}
							// 15分ごとにカウントが初期化される。
							else if (timedif > 900) {
								info.cnt = 0;
								info.mode = 'dialog';
								console.log(timedif + 'sec [Initializing... cnt]');
								return Promise.resolve(['default', info]);
							} else {
								return Promise.resolve(['default', info]);
							};
							break;
					};
				};
			}).catch((e) => {
				console.log('[ERR][MODEcontinue or INITIALIZE]');
				console.log(e);
				return Promise.resolve(['error', info]);
			// }).then((arg) => {
			// 	var mode = arg[0];
			// 	var info = arg[1];
			// 	//キーワード抽出部
			// 	return TFIDF_py(text, '').then((r) => {
			// 		r = r.replace('\n', '');
			// 		keywords = r.split('<JOIN>');
			// 		info.kex = keywords
			// 		return Promise.resolve([mode, info]);
			// 	}).catch((e) => {
			// 		console.log('[ERR][TFIDF_py]');
			// 		console.log(e);
			// 		return Promise.resolve([mode, info]);
			// 	});
			}).then((arg) => {
				var mode = arg[0];
				var info = arg[1];
				// print(info)
				// ------------------------------------ 
				// LANGUAGE SELECTION
				if (_.contains(tags, '日本語リプ')) {
					info.langed = 'ja';
					info.mode = 'replyFL';
					return Promise.resolve([mode, info]);
				} else if(_.contains(tags, '英語リプ')) {
					info.langed = 'en';
					info.mode = 'replyFL';
					return Promise.resolve([mode, info]);
				} else if(_.contains(tags, 'ドイツ語リプ')) {
					info.langed = 'de';
					info.mode = 'replyFL';
					return Promise.resolve([mode, info]);
				} else if (_.contains(tags, 'スペイン語リプ')) {
					info.langed = 'es';
					info.mode = 'replyFL';
					return Promise.resolve([mode, info]);
				} else if (_.contains(tags, 'アラビア語リプ')) {
					info.langed = 'ar';
					info.mode = 'replyFL';
					return Promise.resolve([mode, info]);
				} else if (_.contains(tags, 'ロシア語リプ')) {
					info.langed = 'ru';
					info.mode = 'replyFL';
					return Promise.resolve([mode, info]);
				} else if ((_.contains(tags, '韓国語リプ')) || (_.contains(tags, '朝鮮語リプ'))) {
					info.langed = 'ko';
					info.mode = 'replyFL';
					return Promise.resolve([mode, info]);
				} else if (_.contains(tags, 'フランス語リプ')) {
					info.langed = 'fr';
					info.mode = 'replyFL';
					return Promise.resolve([mode, info]);
				} else if (_.contains(tags, '英会話')) {
					info.mode = 'verbal_learning'
					info.lang = 'en';
					info.langed = 'en';
					return Promise.resolve([mode, info]);
				} else if (_.contains(tags, 'ドイツ語会話')) {
					info.mode = 'verbal_learning'
					info.lang = 'de';
					info.langed = 'de';
					return Promise.resolve([mode, info]);
				} else if (_.contains(tags, 'ロシア語会話')) {
					info.mode = 'verbal_learning'
					info.lang = 'ru';
					info.langed = 'ru';
					return Promise.resolve([mode, info]);
				} else if (info.lang != 'ja'){
					return detectLang(text).then((result) => {
						info.langed = result;
						if (result != 'ja') {
							return Promise.resolve(['dialogFL', info]);
						} else {
							return Promise.resolve([mode, info]);
						};
					}).catch((e) => {
						console.log(e);
						return Promise.resolve([mode, info]);
					});
				} else {
					return Promise.resolve([mode, info]);
				};
			}).catch((e) => {
				console.log('[ERR][LANGUAGE SELECTION]');
				console.log(e);
				return Promise.resolve(['error', info]);
			}).then((arg) => {
				var mode = arg[0];
				var info = arg[1];
				// ------------------------------------ 
				// COMMAND STARTER
				console.log(mode);
				if(mode != 'default'){
					return Promise.resolve([mode, info]);
				} else if (_.contains(tags, 'clearAuth')) {
					return Promise.resolve(['clearAuth', info]);
				} else if (_.contains(tags, 'quoteRestriction')) {
					return Promise.resolve(['quoteRestriction', info]);
				} else if (_.contains(tags, 'delReactRestriction')) {
					return Promise.resolve(['delReactRestriction', info]);
				} else if (_.contains(tags, 'interruptRestriction')) {
					return Promise.resolve(['interruptRestriction', info]);
				} else if (_.contains(tags, 'analFavWord') ||_.contains(tags, 'マイブームなことば')) {
					return Promise.resolve(['analFavWord', info]);
				} else if (_.contains(text, 'うみもん') || _.contains(tags, 'うみもん')) {
					mode = 'twmon';
					info.mode = mode;
					return Promise.resolve([mode, info]);
				} else if (_.contains(text, 'しりとり') ||_.contains(tags, 'しりとり')) {
					mode = 'srtr';
					info.mode = mode;
					return Promise.resolve([mode, info]);
				} else if (_.contains(tags, 'QA')) {
					return Promise.resolve(['QA', info]);
				} else if (_.contains(text, 'おみくじ')) {
					return Promise.resolve(['おみくじ', info]);
				} else if (_.contains(tags, 'おうむ返し') || _.contains(tags, 'Parrot')) {
					return Promise.resolve(['Parrot', info]);
				} else if (_.contains(tags, 'フォロバ')) {
					return Promise.resolve(['followback', info]);
				} else if (_.contains(tags, '構造化モデリング') || _.contains(tags, 'ISM')) {
					mode = 'ISM';
					info.mode = mode;
					return Promise.resolve([mode, info]);
				} else if (_.contains(tags, '実現性評価') || _.contains(tags, 'FAT')) {
					mode = 'FAT';
					info.mode = mode;
					return Promise.resolve([mode, info]);
				} else if (_.contains(tags, 'だいすき')) {
					return Promise.resolve(['daisuki', info]);
				} else if (_.contains(tags, '形態素解析') || _.contains(tags, 'MA')) {
					return Promise.resolve(['MeCab', info]);
				} else if  (_.contains(tags, '言語判定') || _.contains(tags, 'detectLang')){
					return Promise.resolve(['detectLang', info]);
				} else if (_.contains(tags, '翻訳') || _.contains(tags, 'translate')) {
					return Promise.resolve(['translate', info]);
				} else if (_.contains(tags, 'eStat') || _.contains(tags, '政府統計')) {
					mode = 'eStat';
					info.mode = mode;
					return Promise.resolve([mode, info]);
				} else if (_.contains(tags, '危険判定') || _.contains(tags, '有害情報判定') || _.contains(tags, 'sensitiveCheck')) {
					return Promise.resolve(['sensitiveCheck', info]);
				} else if (_.contains(tags, 'キーワード') || _.contains(tags, '感性解析') || _.contains(tags, 'nazukiSA') || _.contains(tags, '言語解析')) {
					return Promise.resolve(['nazukiSA', info]);
				} else if (_.contains(tags, 'debug')) {
					return Promise.resolve(['debug', info]);
				} else if (_.contains(tags, 'suser')) {
					return Promise.resolve(['suser', info]);
				} else if (_.contains(tags, '半角') || _.contains(tags, 'かよちんモノマネ') || _.contains(tags, '花陽')) {
					return Promise.resolve(['han', info]);
				} else if (_.contains(tags, '分類') || _.contains(tags, 'classify')) {
					return Promise.resolve(['classify', info]);
				} else if (_.contains(tags, '学習') || _.contains(tags, 'learn')) {
					return Promise.resolve(['learn', info]);
				} else if (_.contains(tags, '構文解析') || _.contains(tags, 'CaboCha') || _.contains(tags, 'SyntacticAnalysis')) {
					return Promise.resolve(['SyntacticAnalysis', info]);
				// ------------------------------------ 
				// LIMITATION
				} else if (info.auth == 'suser') {
					console.log('<<<<SUPERUSER auth>>>>>');
					return Promise.resolve(['default', info]);
				} else if (info.replycnt > 5) {
					return Promise.resolve(['replycnt', info]);
				} else if (timedif < 5) {
					return Promise.resolve(['tooFreq', info]);
				} else if (cnt > 10) {
					return Promise.resolve(['cnt', info]);
				} else {
					return Promise.resolve(['default', info]);
				};
			}).catch((e) => {
				console.log('[ERR][tagCOMMAND]');
				console.log(e);
				return Promise.resolve(['error', info]);
			}).then((arg) => {
				var mode = arg[0];
				var info = arg[1];
				return Promise.resolve([mode, info]);
			});
		}).then((arg) => {
			var func = arg[0];
			var info = arg[1];
			var tags = info.tags;
			var ans = 'よくわかりませんでした。';
			// c = 'learn';
			print('[...][answer][' + func + ']@' + screen_name);
			switch (func) {
				default:
					return trigram_py(text).then((ans) => {
						umians = ans.replace('<人名>', info.name)
							return Promise.resolve([umians, info]);
					});
					break;
				case 'learn':
					return savePhrase({
						phrase: text,
						character: char,
						s_type: 'test',
						react_sense: '無',
						author: info.screen_name
					}).then((phrase) => {
						console.log(phrase);
						info.mode = 'dialog';
						info.waiting = text;
						ans = '(「' + text + '」......を覚えました。今度使ってみますね。)';
						// \nこれはどういう文章に投げかけるフレーズなんでしょう？(好奇心)';
						return Promise.resolve([ans, info]);
					}); break;
				// case 'modify':
				// 	return savePhrase({
				// 		phrase: text,
				// 		character: char,
				// 		s_type: 'test',
				// 		react_sense: '無',
				// 		author: info.screen_name
				// 	}).then((phrase) => {
				// 		console.log(phrase);
				// 		info.mode = 'dialog';
				// 		info.waiting = text;
				// 		ans = '(「' + text + '」......を覚えました。)';
				// 		// \nこれはどういう文章に投げかけるフレーズなんでしょう？(好奇心)';
				// 		return Promise.resolve([ans, info]);
				// 	}); break;
				case 'learn.q':
					return nazukiSA_Main(s)
					.then((nazuki) => {
						// console.log(nazuki);
						var modPhrase = info.waiting;
						var sense = nazuki['intx'][2];
						var key = nazuki['kex'][0][0];
						// var tab = nazuki['tabx'][0][0];
						if (sense == '無' & nazuki['tabx'][0] != ''){sense = nazuki['tabx'][0][0];};
						return savePhrase({
							phrase: modPhrase,
							react_sense: sense,
							react_keyword: key
						}).then((phrase) => {
							console.log(phrase)
							info.mode = 'dialog';
							info.waiting = '';
							var sense = phrase.react_sense;
							if (sense == '無'){sense = '全般';};
							if (key == ''){anskey = 'いろいろなもの'}
							ans = anskey + 'に関する' + sense + 'な感情の文に対して使うフレーズなのですね。教えていただきありがとうございます。';
							return Promise.resolve([ans, info]);
						});
					}); break;
				case 'QA':
					return QA(text).then((data) => {
						if (data == undefined) {
							return Promise.resolve([ans, info]);
						} else {
							// console.log(data);
							var qaanswer = data.answers[0];
							if (qaanswer == undefined) {
								console.log(qaanswer);
								ans = data.message.textForDisplay;
								return Promise.resolve([ans, info]);
							} else {
								ans = qaanswer.answerText;
								if (ans != undefined) {
									ans = 'おそらく' + ans + '…だと思いますよ？';
									return Promise.resolve([ans, info]);
								};
							};
						};
					});
					break;
				case 'Parrot':
					return Promise.resolve([text, info]);
					break;
				case 'おみくじ':
					return getPhrase({character: char, s_type: 'おみくじ'})
					.then((result) => {
						// console.log(result)
						ans = result.phrase;
						info.mode = 'dialog';
						return Promise.resolve([ans, info]);
					}).catch((e) => {
						return Promise.resolve(['......', info]);
					});
					break;
				case 'interrupt':
					var infomode = info.mode;
					switch (infomode) {
						case 'learn.q':
							result = 'まだ、私とのお話の途中ですよ？#学習';
							return Promise.resolve([result, info]);
							break;
						case 'srtr':
							result = 'まだ、私とのしりとりの途中ですよ？諦めたのですか？しりとりを終えるには「しりとりおわり」と言ってくださいね。#しりとり ';
							return Promise.resolve([result, info]);
							break;
						case 'twmon':
							result = 'まだ、うみもんゲームの途中ですよ？私を独りにしないでください...ゲームを終えるには「おわり」と言ってくださいね。#うみもん ';
							return Promise.resolve([result, info]);
							break;
						case 'FAT':
							result = 'まだ、実現性評価チュートリアルの途中ですよ？他の人とお話している場合じゃないです。FATを終えるには「おわり」と言ってくださいね。#実現性評価 ';
							return Promise.resolve([result, info]);
							break;
						default:
							return getPhrase({character: char, s_type: 'interrupt'})
							.then((result) => {
								// console.log(result)
								ans = result.phrase;
								info.mode = 'dialog';
								return Promise.resolve([ans, info]);
							}).catch((e) => {
								return Promise.resolve(['......', info]);
							});
							break;
						};
					break;
				case 'clearAuth':
					info.auth = 'user';
					ans = 'すべての権限及び制限を解除しました。\n再度権限及び制限変更を行う場合は、 #quoteRestriction #delReactRestriction #interruptRestriction #suserを送ってください。#clearAuth';
					return Promise.resolve([ans, info]);
					break;
				case 'quoteRestriction':
					var auth = info.auth
					console.log(auth);
					if (!_.contains(auth, 'quoteRestriction')) {
						info.auth = info.auth + '.quoteRestriction'
						ans = '引用を制限しました。今後引用RTの対象から除外されます。\n制限を解除する場合は、再度 #quoteRestriction を送ってください。';
					} else {
						info.auth = auth.replace('.quoteRestriction', '');
						ans = '引用制限を解除しました。今後引用RTの対象に復帰します。\n再度制限をする場合は、 #quoteRestriction を送ってください。';
					};
					return Promise.resolve([ans, info]);
					break;
				case 'delReactRestriction':
					var ans;
					var auth = info.auth
					console.log(auth);
					if (!_.contains(auth, 'delReactRestriction')) {
						console.log(auth);
						info.auth = info.auth + '.delReactRestriction'
						ans = 'tweet削除に対するリアクションを制限しました。今後対象から除外されます。\n制限を解除する場合は、再度 #delReactRestriction を送ってください。';
					} else {
						info.auth = auth.replace('.delReactRestriction', '');
						ans = 'tweet削除に対するリアクション制限を解除しました。今後対象に復帰します。\n再度制限をする場合は、 #delReactRestriction を送ってください。';
					};
					return Promise.resolve([ans, info]);
					break;
				case 'interruptRestriction':
					var ans;
					var auth = info.auth
					console.log(auth);
					if (!_.contains(auth, 'interruptRestriction')) {
						info.auth = info.auth + '.interruptRestriction'
						ans = '会話割り込みを制限しました。今後対象から除外されます。\n制限を解除する場合は、再度 #interruptRestriction を送ってください。';
					} else {
						info.auth = auth.replace('.interruptRestriction', '');
						ans = '会話割り込み制限を解除しました。今後対象に復帰します。\n再度制限をする場合は、 #interruptRestriction を送ってください。';
					};
					return Promise.resolve([ans, info]);
					break;
				case 'dialogFL':
					var lang = info.lang;
					info.mode = 'dialog';
					return translate(text, 'ja').then((tltext) => {
						console.log(tltext);
						return trigram_py(text).then((ans) => {
							info.mode = 'dialogFL';
							return Promise.resolve([ans, info]);
						});
					})
					break;
				case 'replyFL':
					var langed = info.langed;
					var result = '( •̀ ᴗ •́ )\n次回より、[' + langed + ']でリプライします。\n「init」で初期化するか、5分間放置すれば自動で元の言語に戻ります。\n私からのリプライのみ翻訳されます。私に返す言語は日本語でOKです。\nなお、自動機械翻訳のため責任はとれないです。';
					return Promise.resolve([result, info]);
					break;
				case 'MeCab':
					return new Promise((resolve, reject) => {
						resolve();
					}).then((arg) => {
						var form = 'all';
						var mode = 'n';
						var except = 'none';
						var formlist = [];
						if (_.contains(tags, '名詞')) { formlist.push('名詞'); };
						if (_.contains(tags, '動詞')) { formlist.push('動詞'); };
						if (_.contains(tags, '形容詞')) { formlist.push('形容詞'); };
						if (_.contains(tags, '副詞')) { formlist.push('副詞'); };
						if (_.contains(tags, '感動詞')) { formlist.push('感動詞'); };
						form = formlist.join(',');
						if (_.contains(tags, '原形')) { mode = 'g'; };
						if (_.contains(tags, 'カタカナ')) { mode = 'k'; };
						if (_.contains(tags, '詳細')) { mode = 'detail'; };
						if (_.contains(tags, 'リスト')) { mode = 'n'; };

						return getMA(text, form, mode, except).then((result) => {
							var ans = result.join(' | ');
							info.cnt = 0;
							info.mode = 'dialog';
							return Promise.resolve([ans, info]);
						}).catch((e) => {
							console.log(e, 'at [MA3]');
							info.mode = 'dialog';
							result = '形態素解析できませんでした...'
							return Promise.resolve([result, info]);
						});
					}).catch((e) => {
						info.mode = 'dialog';
						return Promise.resolve([result, info]);
					}); break;
				case 'SyntacticAnalysis':
					return new Promise((resolve, reject) => {
						resolve();
					}).then((arg) => {
						if (_.contains(tags, 'tree')) {
							return SyA_py(text, 'SyA.getTree()').then((result) => {
								var ans = '各単語の係り受けのツリー図を描いてみました。( •̀ ᴗ •́ )\n' + result;
								return Promise.resolve([ans, info]);
							});
						} else if (_.contains(tags, 'pairs')) {
							return SyA_py(text, 'SyA.showPairs()').then((result) => {
								var ans = '各単語の係り受けのペアはこうなっているのではありませんか？\n' + result;
								return Promise.resolve([ans, info]);
							});
						} else {
							return SyA_py(text, 'showPairs').then((result) => {
								var ans = '各単語の係り受けのペアはこうなっているのではありませんか？\n' + result;
								return Promise.resolve([ans, info]);
							});
						};
					}).catch((e) => {
						console.log(e, 'at [SyA]');
						var ans = 'うまく解析できませんでした... (SyntacticAnalysis.py with CaboCha)';
						return Promise.resolve([ans, info]);
					});
					break;
				case 'ISM':
					return new Promise((resolve, reject) => {
						resolve();
					}).then((arg) => {
						var pyfunc = 'ISM.result()';
						if (_.contains(tags, '詳細')) { pyfunc = 'ISM.detail()'; };
						return ISM_py(text, pyfunc).then((result) => {
							var ans = '構造化モデリングを代わりに計算してあげます。( •̀ ᴗ •́ )\n 行列とかブール演算とか穂乃果じゃできないでしょうから。\n' + result;
							return Promise.resolve([ans, info]);
						});
					}).catch((e) => {
						console.log(e, 'at [ISM.py]');
						var ans = 'うまく解析できませんでした... 循環している可能性がありませんか? (ISM with python)';
						return Promise.resolve([ans, info]);
					});
					break;
				case 'sensitiveCheck':
					return sensitiveCheck(text).then((result) => {
						var dngRate = 0;
						var dngID;
						if (result.quotients != undefined) {
							var quocnt = result.quotients.length;
							var ansmap = result.quotients.map((quo) => {
								var cluster = quo.cluster_name;
								dngRate = quo.quotient_rate;
								var dngID = quo.quotient_id;
								var ret = dngRate + ' %分「' + cluster + '」(' + dngID + ')\n';
								return ret;
							});
							var ans = ansmap + 'に関する内容を含んでいます。';
							ans = ans.replace('\n,', '\n').replace('\n,', '\n').replace('\n,', '\n').replace('\n,', '\n');
							return Promise.resolve([ans, info]);
						} else {
							ans = 'このツイートは無害です。';
							return Promise.resolve([ans, info]);
						};
					}).catch((e) => {
						var ans = 'うまく有害情報を判定できませんでした...';
						return Promise.resolve([ans, info]);
					}); break;
				case 'detectLang':
					return new Promise((resolve, reject) => {
						resolve();
					}).then((arg) => {
						return detectLang(text).then((result) => {
							var ans = 'この文章の言語は...\n' + result + '\nですッ！！';
							return Promise.resolve([ans, info]);
						})
					}).catch((e) => {
						console.log(e, 'at [MST.api]');
						var ans = 'うまく言語判定できませんでした...';
						return Promise.resolve([ans, info]);
					});
					break;

				case 'translate':
					return new Promise((resolve, reject) => {
						resolve();
					}).then((arg) => {
						var lang = 'en';
						if (_.contains(tags, '日本語')) { lang = 'ja'; };
						if (_.contains(tags, 'スペイン語')) { lang = 'es'; };
						if (_.contains(tags, 'ドイツ語')) { lang = 'de'; };
						if (_.contains(tags, 'フランス語')) { lang = 'fr'; };
						if (_.contains(tags, 'アラビア語')) { lang = 'ar'; };
						if (_.contains(tags, 'ロシア語')) { lang = 'ru'; };
						return translate(text, lang).then((result) => {
							var ans = '翻訳結果です。\n' + result + '\n[=>' + lang;
							return Promise.resolve([ans, info]);
						})
					}).catch((e) => {
						console.log(e, 'at [MST.api]');
						info.mode = 'dialog';
						var ans = 'うまく翻訳できませんでした...';
						return Promise.resolve([ans, info]);
					});
					break;

				case 'srtr':
					return new Promise((resolve, reject) => {
						resolve();
					}).then((arg) => {

						if (info.cnt > 10){
							text = 'しりとりおわり';
						};
						return shiritori_py(text, screen_name).then((result) => {
							if ((/#END/g).test(result)) {
								info.mode = 'dialog';
								info.cnt = 0;
								result = result.replace('#END', '');
							} else if ((/#MISS/g).test(result)) {
								result = result.replace('#MISS', ''); //ミスするとcntがひとつ加算される。
								info.mode = 'srtr';
								if (info.cnt > 3) { info.cnt = 20; };
							} else {
								info.cnt = 0;
								info.mode = 'srtr';
							};
							console.log(result);
							return Promise.resolve([result, info]);
						});
					}).catch((e) => {
						console.log(e, 'at [srtr.py]');
						result = '( •̀ ᴗ •́ )しりとりしたかったです...';
						info.mode = 'dialog';
						return Promise.resolve([result, info]);
					});
					break;
				case 'twmon':
					info.mode = 'dialog';
					result = 'ただいま工事中です...... しばらくお待ち下さい。';
					return Promise.resolve([result, info]);
					// return new Promise((resolve, reject) => {
					// 	resolve();
					// }).then((arg) => {
					// 	info.cnt = 0;
					// 	if (text == 'おわり') {
					// 		info.mode = 'dialog';
					// 		result = '\n( •̀ ᴗ •́ )強制終了しました。またあそんでくださいね。';
					// 		return Promise.resolve([result, info]);
					// 	}''
					// 	var me = info._id
					// 	return twmon_py(me, text).then((result) => {
					// 		if ((/#EXP/g).test(result)) {
					// 			var Expsplit = result.split('#EXP');
					// 			var expstr = Expsplit[1]
					// 			info.exp = Number(expstr);
					// 			result = Expsplit[0];
					// 		};
					// 		if ((/#END/g).test(result)) {
					// 			info.mode = 'dialog';
					// 			result = result.replace('#END', '');
					// 		} else {
					// 			info.mode = 'twmon';
					// 		};
					// 		return Promise.resolve([result, info]);
					// 	});
					// }).catch((e) => {
					// 	console.log(e, 'at [pymon.py]');
					// 	result = '( •̀ ᴗ •́ )おとのきざかモンスター`s[海未](通称:うみもん)のせかいへようこそ。[β版]\n進行役の園田海未です。私となかよくしたり、ふぁぼったり、ツイートしたり、ゲームであそんだりすると強くなれますよ。\n「たたかう」と返信して、さぁ修行ですっ！！';
					// 	info.mode = 'twmon';
					// 	return Promise.resolve([result, info]);
					// });
					break;
				case 'followback':
					follow(char, screen_name)
					var result = '( •̀ ᴗ •́ )「フォロバ」コマンドでフォローしました。\n- このbotは、海未ちゃんがAIをめざすというコンセプトのもと開発進行中のラブライブ！非公式多機能botです。\nーーーーーー\n- ほぼすべての動作が、プログラムによる自動機械生成です(作者発言には目印)。\nーーーーーー\n- 娯楽・実務ともに様々な機能があります。取扱説明書( https://github.com/xxxx'
					info.cnt = 0;
					info.mode = 'followback'
					console.log('REfollowed!! ' + screen_name);
					return Promise.resolve([result, info]);
					break;
				case 'daisuki':
					return createTweet_py('Daisuki').then((result) => {
						info.mode = 'dialog';
						return Promise.resolve([result, info]);
					});
					break;
				case 'analFavWord':
					return createTweet_py('analFavWord', screen_name).then((result) => {
						info.mode = 'dialog';
						return Promise.resolve([result, info]);
					});
					break;
				case 'han':
					return any2hankana(text).then((result) => {
						var ans = 'えっ、花陽のモノマネですか...? 。うぅ...恥ずかしいですけど、仕方ありませんね。\n「 ' + result + ' 」\n ど、どうですか?';
						return Promise.resolve([ans, info]);
					}).catch((e) => {
						console.log(e, 'at [han]');
						var ans = '変換に失敗しました...'
						return Promise.resolve([ans, info]);
					}); break;

				case 'classify':
					return clusterAnalysis(text).then((result) => {
						if (result.count == 0) {
							var ans = '分類できませんでした。ごめんなさい。';
						} else {
							var cluster = result.clusters[0].cluster_name;
							if (cluster != undefined) {
								console.log(cluster);
								ans = cluster + 'についてですか? ';
							};
						};
						return Promise.resolve([ans, info]);
					});
					break;
				case 'FAT':
					info.cnt = 0
					return assessSHF_py(text, screen_name).then((result) => {
						if ((/#END/g).test(result)) {
							info.mode = 'dialog';
							result = result.replace('#END', '');
						} else {
							info.mode = 'FAT';
						};
						return Promise.resolve([result, info]);
					});
					break;
				case 'nazukiSA':
					return nazukiSA(text).then((result) => {
						var cmdline = text.split(' ');
						var param0 = cmdline[0];
						var param1 = cmdline[1];
						var nazukiintx = Dics.nazukiSA.intx;
						var intxPromisify = new Promise((resolve, reject) => {
							var intxlist = result['intx-results'];
							resolve(intxlist);
						}).then((intxlist) => {
							return Promise.all(intxlist.map((intx) => {
								var relations = intx['relations'].map((r) => { return r["surface"]; });
								var senseID = intx['sense-id'];
								return Promise.resolve([nazukiintx[senseID], relations]);
							}));
						});
						var kexPromisify = new Promise((resolve, reject) => {
							var kexlist = result['kex-results'];
							resolve(kexlist);
						}).then((kexlist) => {
							return Promise.all(kexlist.map((kex) => {
								var keyword = kex["surface"];
								var keyscore = kex['score'];
								return Promise.resolve([keyword, keyscore]);
							}));
						});
						return Promise.all([intxPromisify, kexPromisify])
							.then((result) => {
								var intx = result[0];
								var kex = result[1];
								console.log(intx, kex);
								if (intx == '') {
									var intxphrase = '感性情報は見当たらないようですね。'
								} else {
									var intx0 = intx[0];
									var intxsense = intx0[0];
									switch (param1) {
										default:
											var sense = intxsense[2];
											break;
										case '中':
											var sense = intxsense[1];
											break;
										case '大':
											var sense = intxsense[0];
											break;
									};
									intxphrase = '要するに、' + intx0[1].join(' => ') + 'は「' + sense + '」という思いなのですね。';
									if (intx0[1] == '') { intxphrase = '要するに、「' + sense + '」という思いなのですね。'; };
								};

								if (kex == '') {
									var kexphrase = 'キーワードは見当たらないようですね。'
								} else {
									kexphrase = 'キーワードおよび重要度は以下の通りです。:\n' + kex.map((akex) => { return akex.join(':') }).join('\n');
								};
								return Promise.resolve([intxphrase, kexphrase]);
							}).then((arg) => {
								var intxphrase = arg[0];
								var kexphrase = arg[1];
								ans = intxphrase + '\n' + kexphrase;
								if (_.contains(tags, 'キーワード')) { var ans = kexphrase; };
								if (_.contains(tags, '感性解析')) { var ans = intxphrase; };
								return Promise.resolve([ans, info]);
							});
					}).catch((e) => {
						console.log(e, 'at [nazukiSA]');
						var ans = 'この文章では解析できそうにありません...';
						return Promise.resolve([ans, info]);
					});
					break;
				case 'eStat':
					var Q0sep = text.split('\n');
					var limitcnt = Q0sep[1];
					if (limitcnt == undefined) { limitcnt = 10; };
					return eStatSearch(Q0sep[0], limitcnt).then((stats) => {
						var errorMsg = stats['RESULT']['ERROR_MSG'];
						console.log(stats);
						var statsNum = stats['DATALIST_INF']['NUMBER'];
						var datas = stats['DATALIST_INF']['TABLE_INF'];
						var statisticsnames = datas.map((data) => {
							var statName = data['STATISTICS_NAME'];
							var statID = data['@id'];
							var ans = statName + ' [' + statID + ']';
							return ans;
						});
						var statIDs = datas.map((data) => { return data['@id'] });
						var ans = '政府の統計によれば、全部で' + statsNum + '件の統計データがあります。\nこのうち' + limitcnt + '件を抽出しました。以下の通りです。\n- ' + statisticsnames.join('\n- ') + '\n もっと知りたいのですか？ でしたら番号を教えてください。';
						console.log(ans);
						info.mode = 'waiting.eStat';
						return Promise.resolve([ans, info]);
					}).catch((e) => {
						console.log(e, 'at [eStat]');
						var ans = 'うまく見つかりませんでした...(β機能eStat)';
						return Promise.resolve([ans, info]);
					}); break;

				case 'debug':
					return new Promise((resolve, reject) => {
						if (info.auth != 'suser') { reject('not_suser'); };
						resolve();
					}).then(() => {
						var Q0sep = text.split('\n');
						var p1 = Q0sep[1];
						var p2 = Q0sep[2];
						var p3 = Q0sep[3];
						if (_.contains(tags, 'help')) {
							var ans = '#modify_info\n#show_info\n#learn_FixedPhrase\n#show_FixedPhrase\n#reboot\n#help';
						} else if (_.contains(tags, 'tweet4me')) {
							ans = text;
						} else if (_.contains(tags, 'modify_info')) {
							info[p1] = p2;
							ans = p1 + 'は、' + p2 + 'に変更されました。';
						} else if (_.contains(tags, 'show_info')) {
							ans = JSON.stringify(info).replace(/,/g, ',\n');
						} else if (_.contains(tags, 'learn_FixedPhrase')) {
							Dics.Umiphrases.push(text);
							writeJSON(Dics, Dics_PLACE);
							ans = '「 ' + text + ' 」\nを定型文としてメモリしました。';
						} else if (_.contains(tags, 'show_FixedPhrase')) {
							ans = Dics.Umiphrases.join('\n');
						} else if (_.contains(tags, 'reboot')) {
							setTimeout(() => {
								spawnPM2('restart', 'all');
							}, 10000);
							ans = '10秒後、pm2による自動再起動に以降します...';
						} else {
							ans = 'debugmodeです。\nコマンドのハッシュタグに指定の命令を書いてリトライしてください。#debug #modify_info\n#show_info\n#learn_FixedPhrase\n#show_FixedPhrase\n#reboot\n#help';
						};
						return Promise.resolve([ans, info]);
					}).catch((e) => {
						console.log(e, 'at [debug]');
						if (info.auth != 'suser') {
							var ans = 'debugmodeです。suser以外は使用できません。\nコマンドのハッシュタグに指定の命令を書いてリトライしてください。#debug #help';
						} else {
							ans = 'debugmodeです。\nコマンドのハッシュタグに指定の命令を書いてリトライしてください。#debug #help';
						};
						return Promise.resolve([ans, info]);
					}); break;
				case 'suser':
					return new Promise((resolve, reject) => {
						resolve();
					}).then(() => {
						if (text == 'askg') {
							info.auth = 'suser';
							var ans = 'Congratulation!!, YOU ARE SUSER!!';
						} else {
							ans = 'invalid password... please try again.';
						};
						return Promise.resolve([ans, info]);
					}).catch((e) => {
						console.log(e, 'at [suser]');
						var ans = 'suser auth; please try again...'
						return Promise.resolve([ans, info]);
					}); break;
				case 'newAccount':
					console.log('hello new account')
					info = {};
					info._id = screen_name;
					info.screen_name = screen_name;
					info.name = screen_name;
					info.usr_id = '';
					info.cnt = 0;
					info.lang = 'ja';
					info.langed = 'ja';
					info.totalcnt = 1;
					info.replycnt = 0;
					info.context = '';
					info.mode = "dialog";
					info.auth = "user";
					info.friends_cnt = 0;
					info.followers_cnt = 0;
					info.statuses_cnt = 0;
					info.fav_cnt = 0;
					info.status_id = '';
					info.exp = 0;
					var result = 'はじめまして。よろしくお願いしますね。(ユーザー情報をセットアップしました。)';
					return Promise.resolve([result, info]);
					break;
				case 'eStat.getTable':
					info.mode = "dialog";
					return answerDAPI(text, screen_name, info, 'eStat.getTable').then((arg) => {
						console.log(arg);
						var ans = arg[0];
						info = arg[1];
						return Promise.resolve([ans, info]);
					}).catch((e)=>{
						result = '指定の統計はありません。';
						return Promise.resolve([result, info]);
					});
					break;
				case 'timeup':
					result = 'タイムアップです。また次の機会にしませんか？';
					info.mode = "dialog";
					return Promise.resolve([result, info]);
					break;
				case 'tooFreq':
					info.mode = "waiting.ignore.tooFreq";
					return getPhrase({character: char, s_type: 'tooFreq'})
					.then((result) => {
						ans = result.phrase;
						return Promise.resolve([ans, info]);
					}).catch((e) => {
						return Promise.resolve(['......', info]);
					});
					break;
				case 'cnt':
					info.cnt = 0;
					info.mode = "waiting.ignore.cnt";
					return getPhrase({character: char, s_type: 'cntOver'})
					.then((result) => {
						ans = result.phrase;
						return Promise.resolve([ans, info]);
					}).catch((e) => {
						return Promise.resolve(['......', info]);
					});
					break;
				case 'replycnt':
					result = _.sample(AnsList);
					info.replycnt = 0;
					info.mode = "waiting.ignore.replycnt";
					return getPhrase({character: char, s_type: 'cntOver'})
					.then((result) => {
						ans = result.phrase;
						return Promise.resolve([ans, info]);
					}).catch((e) => {
						return Promise.resolve(['......', info]);
					});
					break;
				case 'ignore':
					result = 'ignore';
					info.mode = 'dialog';
					return Promise.resolve([result, info]);
					break;
			};
		}).then((arg) => {
			var result = arg[0];
			var info = arg[1];
			var infomode = info.mode;
			if (result == 'ignore'){
				var oMethod = 'ignore';
			} else if (info.mode == 'followback') {
				oMethod = 'dm';
				info.mode = 'dialog'
			} else { 
				oMethod = output; 
			};
			return Promise.resolve([result, info, oMethod]);
		}).then((arg) => {
			// ------------------------------------ 
			// TRANSLATION FUNCTION
			var result = arg[0];
			var info = arg[1];
			var oMethod = arg[2];
			var infomode = info.mode;
			var langed = info.langed;
			if (langed == undefined || langed == null || langed == 'und') { langed = 'ja'; };
			if ((langed != 'ja') && (infomode != 'replyFL')) {
				return translate(result, langed).then((data) => {
					console.log('translated...')
					var ans = data + '\n(' + result + ')\n[auto-translated ja => ' + langed + ']';
					return Promise.resolve([ans, info, oMethod]);
				});
			} else {
				return Promise.resolve([result, info, oMethod]);
			};
		}).then((arg) => {
			var result = arg[0];
			var info = arg[1];
			var oMethod = arg[2];
			var status_id = info.status_id;
			var endTime = new Date();
			// <送信部>場合分け
			switch (oMethod) {
				default:
					console.log('[Answer]↓↓:' + (endTime - startTime) + "ms\n" + result);
					return Promise.resolve([result, info]);
					break;
				case 'crawling':
					console.log('[crawling]', screen_name + result);
					return Promise.resolve([result, info]);
					break;
				case 'ignore':
					console.log('[ignored]', screen_name);
					info.mode = 'dialog';
					return Promise.resolve([result, info]);
					break;
				case 'tweet':
					return tweet(result, char, screen_name, status_id)
						.then((result)=>{
							console.log('tweet SUCCESS!! : ' + result.text);
							info.recentID = result.id_str;
							return Promise.resolve([result, info]);
						});
					break;
				case 'dm':
					return dm(result, char, screen_name)
						.then((result) => {
							console.log('dm SUCCESS!! : ' + result.text);
							return Promise.resolve([result, info]);
						});
					break;
				case 'quote':
					if (_.contains(info.auth, 'quoteRestriction')) {
						result = '#quoteRestriction ' + result;
						return tweet(result, char, screen_name, status_id)
							.then((result) => {
								console.log('tweet SUCCESS!! : ' + result.text);
								info.recentID = result.id_str;
								return Promise.resolve([result, info]);
							});
					} else {
						return quote(result, char, screen_name, status_id)
							.then((result) => {
								console.log('quote RT SUCCESS!! : ' + result.text);
								return Promise.resolve([result, info]);
							});
					};
					break;
			};
		}).then((arg) => {
			var result = arg[0];
			var info = arg[1];
			var infomode = info.mode;
			info.time = nowTime();
			info.cnt++;
			info.totalcnt++;
			// info.twitter.status_id = 0;
			switch(infomode){
				default:
					// console.log('info.mode is not changed');
					break;
				case "waiting.ignore.replycnt":
					info.mode = 'ignore.replycnt';
					console.log('Changed into ignore.replycnt');
					break;
				case "waiting.ignore.cnt":
					info.mode = 'ignore.cnt';
					console.log('Changed into ignore.cnt');
					break;
				case "waiting.ignore.tooFreq":
					info.mode = 'ignore.tooFreq';
					console.log('Changed into ignore.tooFreq');
					break;
				case "replyFL":
					info.mode = 'dialog';
					console.log('Changed into dialog');
					break;
			};
			return Promise.resolve(info);
		}).then((info) => {
			return promiseRetry((retry, tryNum) => {
				return User.upsert(info, {transaction: trnU})
				.then(() => {
					trnU.commit();
				}).then((result) => {
					console.log('[OK][commit.User][' + tryNum + '] ' + info.name + info.screen_name);
				}).catch(retry);
  			}).catch((e) => {
  				console.log('[ERR][commit.User][' + tryNum + '] ' + info.name + '\n' + info);
  				console.log(e)
    			trn.rollback();
  			});
		}).catch((e)=>{
			console.log(e);
		});
	});
};

//////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////
var textFilter = (text) => {
	return Promise.resolve().then(() => {
		var ranges = [
			'\ud83c[\udf00-\udfff]',
			'\ud83d[\udc00-\ude4f]',
			'\ud83b[\ude80-\udeff]',
			'\ud7c9[\ude00-\udeff]',
			'[\u2600-\u27BF]'
		];
		var ex = new RegExp(ranges.join('|'), 'g');
		text = text.replace(ex, '').replace('️️', '').replace('〜', 'ー');
		var cleanText = text.replace(/@[^\s　]+/g, '').replace(/#[^\s　]+/g, '').replace(/^[\s　]+/, '').replace(/http[^\s　]+/g, '').replace(/[\s　]+$/, '');
		return Promise.resolve(cleanText);
	});
};

var simpleTweetFilter = (adata) => {
	return Promise.resolve().then(() => {
		var twtext = adata.text;
		var isRetweet = adata.retweeted_status ? true : false; // 公式RTかどうか
		var isRetweet2 = (/(R|Q)T @[^\s　]+/g).test(twtext); // 非公式RT,QTかどうか
		var isLink = adata.entities.urls.length ? true : false; // リンクを含むかどうか
		/* リンク付きとRTを除外 */
		if (isRetweet || isRetweet2 || isLink) { return; }
		return textFilter(twtext).then((cleanText) => {
			adata.cleanText = cleanText;
			return Promise.resolve(adata);
		});
	});
};

var saveTweets = (query = { screen_name: userdata.screen_name, name: userdata.name, text: rawtext, user_id: userid, bot_id: BOT_ID}) => {
	return sequelizeTWTR.transaction({
		// autocommit :false,
		isolationLevel: Sequelize.Transaction.READ_COMMITTED || "READ COMMITTED"
	}).then((trnT) => {
		var rawtext = query.text;
		var name = query.name;
		return promiseRetry({retries: 5},(retry, tryNum) => {
			return TweetSQL.create(query, {transaction: trnT})
			.then(() => {
				trnT.commit()
				console.log('[OK][commit.TL][' + tryNum + '] ' + name + ':'+ rawtext);
			}).catch(retry);
  		}).catch((err) => {
  			console.log('[ERR][commit.TL][' + tryNum + '] ' + name + ':'+ rawtext);
  			console.log(err)
   			trnT.rollback();
  		});
	});
	// });
};

var saveDMs = (query = { screen_name: userdata.screen_name, name: userdata.name, text: rawtext, user_id: userid, bot_id: BOT_ID}) => {
	// return sequelizeTWTR.sync()
	// .then(() => {
	return sequelizeTWTR.transaction({
		// autocommit :false,
		isolationLevel: Sequelize.Transaction.READ_COMMITTED || "READ COMMITTED"
	}).then((trnD) => {
		var rawtext = query.text;
		var name = query.name;
		return promiseRetry({retries: 5},(retry, tryNum) => {
			return DirectMessageSQL.create(query, {transaction: trnD})
			.then(() => {
				trnD.commit()
				console.log('[OK][commit.DM][' + tryNum + '] ' + name + ':'+ rawtext);
			}).catch(retry);
  		}).catch((err) => {
  			console.log('[ERR][commit.DM][' + tryNum + '] ' + name + ':'+ rawtext);
  			console.log(err)
   			trnD.rollback();
  		});
	});
// });
};

// CronJob
var CronJob = require('cron').CronJob;
var Stream = (char = '', cntRetry = 0, delay = 0) => {
	console.log('Twitter Streaming starting...');
	var twtr;
	var BLACKLIST_ID = ['2805015776', '538086375'];
	switch (char) {
		case 'U':
			var BOT_ID = '2805015776'; //メイン @_umiA
			twtr = twtrU; break;
		case 'R':
			var BOT_ID = '538086375'; //規制回避bot @_rinM
			twtr = twtrR; break;
		default:
			var BOT_ID = '4333033044'; //実験bot @EEE
			// var BOT_ID = '2992260014'; //実験用bot @pEEE
			twtr = twtrE; break;
	};
	return new Promise((resolve, reject) => {
		twtr.stream('user', { with : 'followings', stringify_friend_ids: true}, (stream) => {
			stream.on('data', (rawdata) => {
				// console.log(rawdata)
				if (rawdata.friends_str != undefined) {
					// console.log(rawdata.friends_str);
					return;
				};
				if (rawdata.event == 'unfollow') { //ブロック
					return;
				};
				if (rawdata.delete != undefined) {
					var rnd = Math.random();

					if (rnd < 0.001) {
						var deldatastatus = rawdata.delete.status;
						var id_str = deldatastatus.id_str;
						var user_id = deldatastatus.user_id_str;
						// ユーザーデータ読み込み部
						return User.findOne({ where: { usr_id: user_id } })
							.then((userinfos) => {
								var sql = userinfos['dataValues'];
								var info = sql;
								var screen_name = info['screen_name'];
								if (screen_name == undefined) { return; };
								if (!_.contains(info.auth, 'delReactRestriction')) {
									getPhrase({character: char, s_type: 'delReact'})
									.then((result) => {
										ans = result.phrase;
										return Promise.resolve([ans, info]);
									}).catch((e) => {
										return Promise.resolve(['......', info]);
									}).then((ans) => {
										ans = ans + ' \n消えたツイートid -> ' + id_str + '(joke)[#delReactRestriction で制限可能]'
										return tweet(ans, char, screen_name);
									});
								};
							});
					};
				};
				if (rawdata.user != undefined) {
					var rnd = Math.random();
					var userdata = rawdata.user;
					var userid = userdata.id_str;
					var rawtext = rawdata.text
					saveTweets({ screen_name: userdata.screen_name, name: userdata.name, text: rawtext, user_id: userid, bot_id: BOT_ID});
				// // 	//返答を行う
					var isSendOK = false;
					var isOnetoOne = false;
					var isMimickOK = true;
					if(rnd < 0.01){ isSendOK = true };
					if (((/ぬるぽ/g).test(rawtext))) { isSendOK = true; isOnetoOne = true };
					// if (((/なんでも/g).test(rawtext)) && (rnd < 0.5) && (userid != '3038288276')) { isSendOK = true; isOnetoOne = true };
					switch(char){
						case 'R':
							if (((/@_rinM/g).test(rawtext))) { isSendOK = true };
							if (((/凛ちゃん/g).test(rawtext)) && (rnd < 0.5)) {
								isSendOK = true;
							};
							break;
						case 'U':
							if (_.find(['umiA', 'umia', '海未ちゃんbot', 'おて海未', 'おてつだい海未'], (key) => {
									return _.contains(rawtext, key) == true;
								}) != undefined){
								isSendOK = true;
							};
							if (((/海未ちゃん/g).test(rawtext)) && (rnd < 0.25)) {
								isSendOK = true;
							};
							break;
						default:
							if (((/@_evlP/g).test(rawtext))) { isSendOK = true };
							break;
					};
					if (_.contains(BLACKLIST_ID, userid)) {
						return;
					} else {
						// var isSendOK = true
						if(isSendOK == true){
							var isquoteOK = false;
							if ((/@[^\s　]+/g).test(rawtext) == false) {
								isquoteOK = true;
							};
							// isquoteOK = true;
							return simpleTweetFilter(rawdata).then((data) => {
								if (data.cleanText != undefined){
									var cleanText = data.cleanText;
									var text = cleanText
									var screen_name = data.user.screen_name;
									var status_id = data.id_str;
									// mode = 'crawling';
									mode = '';
									// console.log(rnd)
									// if (rnd < 0.0001 && isquoteOK == true && data.id_str != undefined && mode == 'tweet') {
									// 	return Main(text, screen_name, char, 'quote', data);
									// } else {
									// 	return Main(text, screen_name, char, mode, data);
									// };
								};
							// if (isOnetoOne == true) {
							// 	if (((/ぬるぽ/g).test(rawtext))) {
							// 		var ans = '■━⊂(   •̀ ᴗ •́) 彡 ｶﾞｯ☆`Д´)ﾉ';
							// 		// return tweet(ans, char, screen_name, status_id)
							// 	} else if (((/なんでも/g).test(rawtext))) {
							// 		var ans = '(  •̀ ᴗ •́)っ!! え、今何でもするって言いましたよね？では、一緒に山頂アタックですっ！！';
							// 		// return tweet(ans, char, screen_name, status_id)
							// 	};
							// } else {
							// };
							}).catch((e) => {
								console.log(e);
							});
						};
					};
				};
				// direct message返答
				if (rawdata.direct_message != undefined) {
					var dmdata = rawdata.direct_message;
					var dmtext = dmdata.text;
					var dmsenderdata = dmdata.sender;
					var userid = dmsenderdata.id_str;
					var name = dmsenderdata.name;
					var screen_name = dmsenderdata.screen_name;
					saveDMs({ screen_name: screen_name, name: name, text: dmtext, user_id: userid, bot_id: BOT_ID});
					if (userid == BOT_ID) { 
						return;
					} else {
						return simpleTweetFilter(dmdata).then((data) => {
						var text = data.text
						var screen_name = data.sender_screen_name;
						var status_id = data.id_str;
						// console.log(text, screen_name, status_id)
						// return Main(text, screen_name, char, 'dm', data);
						}).catch((e) => {
							console.log(e);
						});
					};
				};
			});
			stream.on('follow', (rawdata) => {
				// console.log(rawdata.source);
				var follower_name = rawdata.source.screen_name;
				if (rawdata.target.id_str == BOT_ID) {
					// follow(char, follower_name);
					var ans = '( •̀ ᴗ •́ )フォローありがとうございます。フォロバは凍結回避のため、順次手動で行います(#フォロバ 付リプで優先)。気長にお待ちください。娯楽・実務ともに様々な機能でおてつだい！取説を読んで同意の上で…\nさあ、会話しましょう！！';
					return tweet(ans, char, follower_name);
					console.log('REfollowed!! ' + follower_name);
				};
			});
			stream.on('favorite', (rawdata) => {
				// console.log(rawdata);
				var rnd = Math.random();
				if (rnd < 0.15) {
					getPhrase({character: char, s_type: 'favReact'})
					.then((result) => {
						ans = result.framework;
						return Promise.resolve(ans);
					}).catch((e) => {
						return Promise.resolve('......');
					}).then((ans) => {
						ans = ans.replace('<USERNAME>', rawdata.source.name);
						return tweet(ans, char);
					});
				};
			});
			// stream.on('unfavorite', (rawdata) => {
			// 	console.log(rawdata);
			// });
			stream.on('error', (error) => {
				reject(error);
			});
			stream.on('end', (error) => {
				reject(error);
			});
		});
	}).catch((e) => {
		// 再接続処理
		return reconAlgo(cntRetry, delay, 'stream', e)
			.then((arg) => {
				cntRetry = arg[0];
				delay = arg[1];
				setTimeout(() => {
					return Stream(char,cntRetry, delay);
				}, delay);
			}).catch((e) => {
				console.log(e);
			});
	});
};
// 例外処理
// process.on('uncaughtException', (err) => {
// 	console.log('uncaughtException => ' + err);
// });

setTimeout(() => {
	console.log('450秒 自動停止 pm2による再起動に入ります...')
	process.exit();
	// spawnPM2('restart', '0');
}, 450000);
// var util = require('util');
// console.log(util.inspect(process.memoryUsage()));
var s = '' +'致命的やけど大丈夫'
var data = '';
var mode = '';
var Debug = false;
