// 自动生成。仅编辑 Overwrite/source/routing.yaml。source-sha256: e0fc83bee2e1a0a5fb60cf931de4e3299f3149ca65968c29a08a40e9308ca740
// 每次从原始订阅应用；不要将旧运行配置作为输入。
function main(config) {
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new Error("需要原始订阅配置对象");
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
    },
    "GoogleDrive": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/GoogleDrive/GoogleDrive.yaml",
      "path": "./ruleset/GoogleDrive.yaml",
      "interval": 86400
    },
    "GoogleSearch": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/GoogleSearch/GoogleSearch.yaml",
      "path": "./ruleset/GoogleSearch.yaml",
      "interval": 86400
    }
  },
  "rules": [
    "DOMAIN-SUFFIX,antigravity.google,🇯🇵 日本节点",
    "RULE-SET,GoogleDrive,🇯🇵 日本节点",
    "RULE-SET,GoogleSearch,🇯🇵 日本节点",
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
  ],
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
  "dns": {
    "enable": true,
    "enhanced-mode": "fake-ip"
  }
};
  var original = JSON.parse(JSON.stringify(config));
  ["rules", "proxies", "proxy-groups"].forEach(function (key) {
    if (original[key] !== undefined && !Array.isArray(original[key])) throw new Error(key + " 必须是数组");
  });
  ["rule-providers", "dns"].forEach(function (key) {
    if (original[key] !== undefined && (!original[key] || typeof original[key] !== "object" || Array.isArray(original[key]))) throw new Error(key + " 必须是对象");
  });
  var groups = original["proxy-groups"] || [];
  var newGroups = routing["proxy-groups"] || [];
  var names = ["DIRECT", "REJECT"];
  (original.proxies || []).concat(groups, newGroups).forEach(function (item) {
    if (item && typeof item.name === "string") names.push(item.name);
  });
  var targets = routing.rules.map(function (rule) { return rule.split(",")[2]; });
  newGroups.forEach(function (group) { targets = targets.concat(group.proxies || []); });
  var missing = targets.filter(function (name, index, all) { return names.indexOf(name) < 0 && all.indexOf(name) === index; });
  if (missing.length) throw new Error("基础订阅缺少策略组或节点：" + missing.join(", "));
  original["rule-providers"] = Object.assign({}, original["rule-providers"] || {}, routing["rule-providers"]);
  var replaced = newGroups.map(function (group) { return group.name; });
  original["proxy-groups"] = newGroups.concat(groups.filter(function (group) { return replaced.indexOf(group.name) < 0; }));
  original.rules = routing.rules.concat((original.rules || []).filter(function (rule) { return routing.rules.indexOf(rule) < 0; }));
  if (routing.dns) original.dns = Object.assign({}, original.dns || {}, routing.dns);
  return original;
}
