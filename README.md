# linkura-generic-strings-translation


## translation progress

![translation zh-CN](https://img.shields.io/badge/translation_zh--CN-1557%2F1557-blue)
![translation en](https://img.shields.io/badge/translation_en-0%2F1557-blue)
---

## 说明

这是一个linkura翻译模板，用于快速启动翻译项目

该模板提供了一些基本的文件结构和工具，以帮助您更轻松地进行翻译工作。您可以根据自己的需要进行修改和扩展。

主要提供了三大个阶段的翻译

### gentodo

从原始文件中生成中间文件

**推荐**在此阶段就在raw文件夹下生成格式化后的原始文本json文件，这样有助于追踪翻译进度。

### translate

可以编写的自动化翻译工具

提供了基本的大模型api和prompt，您可以根据自己的需要进行修改和扩展。

基本用法如下：


### generate

在 `data` 目录下生成最终翻译文件

```typescript data/*.json format
type i18n = 'zh' ...
type I18n = {
	[key in i18n]: string
}

type TranslatedItem = {
	raw: string,
	translation: I18n,
	author: string,
}

type Data = Array<TranslatedItem>
```

并记录翻译进度
