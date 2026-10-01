// iOS Clash（Hako）JavaScript 分流覆写。
// 根据 stash-routing-overwrite.yaml 转换，保留 ApplePushFallback。
// 启用 DNS 和 Fake-IP，保留订阅其他 DNS 字段、节点和兜底规则。
// 官方入口：main(config)。
function main(config) {
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new Error("覆写需要完整的订阅配置对象");
  }
  var routing = {
    "rule-providers": {
      "Nvidia": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Nvidia/Nvidia.yaml",
        "path": "./rule_provider/Nvidia.yaml",
        "interval": 86400
      },
      "GoogleVoice": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/GoogleVoice/GoogleVoice.yaml",
        "path": "./ruleset/GoogleVoice.yaml",
        "interval": 86400
      },
      "Twitch": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Twitch/Twitch.yaml",
        "path": "./ruleset/Twitch.yaml",
        "interval": 86400
      },
      "Niconico": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Niconico/Niconico.yaml",
        "path": "./ruleset/Niconico.yaml",
        "interval": 86400
      },
      "TikTok": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/TikTok/TikTok.yaml",
        "path": "./ruleset/TikTok.yaml",
        "interval": 86400
      },
      "Reddit": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Reddit/Reddit.yaml",
        "path": "./ruleset/Reddit.yaml",
        "interval": 86400
      },
      "Amazon": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Amazon/Amazon.yaml",
        "path": "./ruleset/Amazon.yaml",
        "interval": 86400
      },
      "Steam": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Steam/Steam.yaml",
        "path": "./ruleset/Steam.yaml",
        "interval": 86400
      },
      "PlayStation": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/PlayStation/PlayStation.yaml",
        "path": "./ruleset/PlayStation.yaml",
        "interval": 86400
      },
      "DouYin": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/DouYin/DouYin.yaml",
        "path": "./ruleset/DouYin.yaml",
        "interval": 86400
      },
      "XiaoHongShu": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/XiaoHongShu/XiaoHongShu.yaml",
        "path": "./ruleset/XiaoHongShu.yaml",
        "interval": 86400
      },
      "BiliBili": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/BiliBili/BiliBili.yaml",
        "path": "./ruleset/BiliBili.yaml",
        "interval": 86400
      },
      "Bing": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Bing/Bing.yaml",
        "path": "./ruleset/Bing.yaml",
        "interval": 86400
      },
      "Porn": {
        "type": "http",
        "behavior": "classical",
        "format": "text",
        "url": "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Porn.list",
        "path": "./rule_provider/Porn.yaml",
        "interval": 86400
      },
      "Instagram": {
        "type": "http",
        "behavior": "classical",
        "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/Instagram/Instagram.yaml",
        "path": "./ruleset/Instagram.yaml",
        "interval": 86400
      }
    },
    "proxy-groups": [
      {
        "name": "ApplePushFallback",
        "type": "fallback",
        "proxies": [
          "🇯🇵 日本节点",
          "DIRECT"
        ],
        "url": "http://www.apple.com/library/test/success.html",
        "interval": 300
      }
    ],
    "rules": [
      "DOMAIN,stun6.chat.bilibili.com,REJECT",
      "IP-CIDR,192.168.18.0/24,DIRECT,no-resolve",
      "IP-CIDR,127.0.0.0/8,DIRECT,no-resolve",
      "IP-CIDR,10.0.0.0/8,DIRECT,no-resolve",
      "IP-CIDR,172.16.0.0/12,DIRECT,no-resolve",
      "DOMAIN-KEYWORD,hosthatch,DIRECT",
      "DOMAIN-KEYWORD,vultr,DIRECT",
      "RULE-SET,Nvidia,🇺🇲 美国节点",
      "RULE-SET,GoogleVoice,🇺🇲 美国节点",
      "RULE-SET,Twitch,🇯🇵 日本节点",
      "RULE-SET,Niconico,🇯🇵 日本节点",
      "RULE-SET,TikTok,🇯🇵 日本节点",
      "RULE-SET,Reddit,🇯🇵 日本节点",
      "RULE-SET,Amazon,🇯🇵 日本节点",
      "RULE-SET,Steam,🇭🇰 香港节点",
      "RULE-SET,PlayStation,🇭🇰 香港节点",
      "RULE-SET,DouYin,DIRECT",
      "RULE-SET,XiaoHongShu,DIRECT",
      "RULE-SET,BiliBili,DIRECT",
      "RULE-SET,Bing,🇺🇲 美国节点",
      "RULE-SET,Porn,🇺🇲 美国节点",
      "RULE-SET,Instagram,🇯🇵 日本节点",
      "DOMAIN-KEYWORD,weixin,DIRECT",
      "DOMAIN-SUFFIX,api.wcc.best,🇯🇵 日本节点",
      "DOMAIN-SUFFIX,sub.xeton.dev,🇯🇵 日本节点",
      "DOMAIN-KEYWORD,ubisoft,🎮 游戏平台",
      "DOMAIN-SUFFIX,amazon.co.jp,🇯🇵 日本节点",
      "DOMAIN-SUFFIX,ssl-images-amazon.com,🇯🇵 日本节点",
      "DOMAIN-SUFFIX,images-na.ssl-images-amazon.com,🇯🇵 日本节点",
      "DOMAIN-SUFFIX,m.media-amazon.com,🇯🇵 日本节点",
      "DOMAIN-SUFFIX,amazon.com,🇯🇵 日本节点",
      "DOMAIN-KEYWORD,afdian,🇯🇵 日本节点",
      "DOMAIN-KEYWORD,tomplay,🇯🇵 日本节点",
      "DOMAIN-KEYWORD,deepl,🇯🇵 日本节点",
      "DOMAIN-KEYWORD,yousician,DIRECT",
      "DOMAIN-SUFFIX,api.deepseek.com,DIRECT",
      "DOMAIN-KEYWORD,javdb,🇺🇲 美国节点",
      "DOMAIN-KEYWORD,perplexity,🇯🇵 日本节点",
      "DOMAIN-SUFFIX,battlenet.com.cn,DIRECT",
      "DOMAIN-KEYWORD,muse,🇯🇵 日本节点",
      "DOMAIN,identity.apple.com,ApplePushFallback",
      "DOMAIN-SUFFIX,akadns.net,ApplePushFallback",
      "DOMAIN-SUFFIX,push.apple.com,ApplePushFallback",
      "DOMAIN-KEYWORD,apple.com.edgekey.net,ApplePushFallback",
      "DOMAIN-SUFFIX,gateway.push.apple.com,ApplePushFallback",
      "DOMAIN-SUFFIX,api.push.apple.com,ApplePushFallback",
      "DOMAIN-SUFFIX,sandbox.push.apple.com,ApplePushFallback",
      "IP-CIDR,17.188.128.0/18,ApplePushFallback,no-resolve",
      "IP-CIDR,17.188.20.0/23,ApplePushFallback,no-resolve",
      "IP-CIDR,17.249.0.0/16,ApplePushFallback,no-resolve",
      "IP-CIDR,17.252.0.0/16,ApplePushFallback,no-resolve",
      "IP-CIDR,17.57.144.0/22,ApplePushFallback,no-resolve",
      "IP-CIDR,2403:300:a42::/48,ApplePushFallback,no-resolve",
      "IP-CIDR,2403:300:a51::/48,ApplePushFallback,no-resolve",
      "IP-CIDR,2620:149:a44::/48,ApplePushFallback,no-resolve",
      "IP-CIDR,2a01:b740:a42::/48,ApplePushFallback,no-resolve"
    ]
  };
  var groups = Array.isArray(config["proxy-groups"]) ? config["proxy-groups"] : [];
  var proxies = Array.isArray(config.proxies) ? config.proxies : [];
  var newGroups = routing["proxy-groups"];
  var names = ["DIRECT", "REJECT"];
  proxies.concat(groups, newGroups).forEach(function (item) {
    if (item && typeof item.name === "string") names.push(item.name);
  });
  var targets = routing.rules.map(function (rule) { return rule.split(",")[2]; });
  newGroups.forEach(function (group) { targets = targets.concat(group.proxies || []); });
  var missing = targets.filter(function (name, index, all) {
    return names.indexOf(name) < 0 && all.indexOf(name) === index;
  });
  if (missing.length) {
    throw new Error("缺少基础订阅策略组或节点，请核对完整名称：" + missing.join(", "));
  }
  var providers = config["rule-providers"] || {};
  Object.keys(routing["rule-providers"]).forEach(function (name) {
    providers[name] = routing["rule-providers"][name];
  });
  config["rule-providers"] = providers;
  var replaced = newGroups.map(function (group) { return group.name; });
  config["proxy-groups"] = newGroups.concat(groups.filter(function (group) {
    return replaced.indexOf(group.name) < 0;
  }));
  var baseRules = Array.isArray(config.rules) ? config.rules : [];
  config.rules = routing.rules.concat(baseRules.filter(function (rule) {
    return routing.rules.indexOf(rule) < 0;
  }));
  config.dns = Object.assign({}, config.dns || {}, {
    enable: true,
    "enhanced-mode": "fake-ip"
  });
  return config;
}
