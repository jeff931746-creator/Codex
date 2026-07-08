# 【FF】军团系统

## 一、 定位

- **社交核心**：将玩家聚拢，通过“红包”、“互助”建立初步联系，为GVG（帮战/攻城战）提供组织基础
- **利益共同体**：通过公会科技、公会商店提供独有的数值成长，强制玩家必须加入公会才能跟上大部队战力
- **冲突制造机**：制造公会之间的矛盾，通过玩法让公会间冲突，刺激玩家竞争

## 二、框架图

<whiteboard token="WRZIweA2kh8j2CbRb0PcqPgZnQd"></whiteboard>

![图片展示了《FF》游戏中的军团系统相关界面。左上角是军团界面，显示军团名称、等级、人数等信息。右侧是军团成员界面，展示成员头像、名称、等级、军团贡献等。下方是军团商店界面，有装备、材料等商品。再下方是军团科技界面，显示科技名称、等级、消耗等。右侧是军团副本界面，有副本名称、等级、难度等信息。最下方是军团战界面，显示战斗双方信息、战力等。这些界面与文档中介绍的军团系统玩法紧密相关，直观呈现了系统功能。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NDBjOTJkZjM1M2M4MjE4NmM0Y2ViOGNkNGQ4NjllOTZfOWQxMTEyMzRjZjc0Njg0YTdhYWNmYjRjYWEwMzZhOTVfSUQ6NzU5NjE4ODM0NDk4ODY4MzIxN18xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)

![图片展示了《蛋仔》游戏中的军团任务界面。左侧为“公会任务”界面，显示“精英识别能力”等任务，有“领取”按钮，任务状态分为未领取、已领取、可领取提示三种。右侧为“军团任务”界面，有“赠送1次体力”和“参与公会捐献3次”任务，前者显示1/1，后者显示3/3，均有“已领取”标识。该图片与文档中介绍军团系统框架的内容相关，直观呈现了游戏中军团任务的设置情况。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZWY1OWRhYTZlNDgwMmFiMzcxMTEzY2I3ZjZhZGUyNzBfZDIzZDM4N2FmYWEzNmY1MzhlYzUwZTFhNjQ2YzIxMGJfSUQ6NzYwMjU1MjQ3MTgyMzY4Mjc2NV8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)

## 三、功能设计

### 军团入口

![图片展示了游戏主界面右下角的收纳按钮，其周围有多个图标，分别为技能、装备强化、装备回收、邮件等。收纳按钮被红色圆圈突出显示。根据上下文，该收纳按钮是军团系统的入口，点击后可打开军团界面，若无军团则打开加入军团界面。此图直观呈现了收纳按钮在主界面的位置，与上下文介绍的入口位置相呼应。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=MzZjZWM2NTQ1YTI3Mzg1NmExODJhZmNiYTliZjU1MzJfYTAwODllMmJiZTcxNTcxNzczYzRkNTg0MmEwMjY3NGVfSUQ6NzU5MzYzNDQwNjI4NDQ0NjkxMV8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)

- 入口位置：主界面右下角收纳按钮
- 沿用功能系统，在对应配置增加解锁条件。解锁后，走常规的解锁提示。
- 点击入口，打开军团界面

  - 如果没有军团，则打开加入军团界面

### 加入军团

![图片展示的是 addCriterion addCriterion了《方舟：生存进化》游戏中加入军团界面。界面上方有“加入公会”标题及“X”关闭按钮。中间区域有“请输入要查询的公会编号”输入框，右侧有“查找”按钮。下方是公会列表，显示了多个公会信息，如“江湖派”“武魂殿”等，每条信息包含公会旗帜、名称、](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NDhjZTFlN2IyNzU0YjBlYzUzNzgxNzljZWVmZWY3ODJfMjFmOTc5Yjk3ODgyZWFlMWNjYTU1OTNjYTdlM2NlMjRfSUQ6NzU5NTU3ODU1NzM4NDkzNjY2NV8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)

- 查找

  - 点击输入框，拉起系统输入，玩家输入编号或名称
  - 点击查找编号或名称包含玩家输入词的军团
  
    - 没有输入，点击查找，提示 请输入要查询的军团名称或编号
    - 查不到对应公会，则提示“查找的军团不存在”
    - 查找成功，则列表筛选出对应的军团
- 军团列表

  - 排序规则：按照军团等级排序，同等级则按照创建时间排序
  - 列表信息包括 军团旗帜、军团名称、军团等级、军团宣言、人数（当前人数/总人数）
  - 加入按钮
  
    - 俱乐部权限为允许快速加入，则按钮为加入。符合入会条件，则按钮点亮，点击直接加入；不符合要求，则按钮置灰，提示公会要求。
    - 不允许快速加入，按钮为申请。符合入会条件，则按钮点亮，点击提示申请成功；不符合要求，则按钮置灰，提示公会要求。
    - 注意
    
      - 申请成功后，公会成员未操作（选择同意或拒绝），则不再允许申请。点击提示“已经申请过该军团，请等待回应”
      - 人数已经的公会依旧显示在列表中，点击提示该军团成员已满
- 创建公会

  - 点击打开，创建军团界面
- 快速加入

  - 点击加入当前可快速加入的军团，如果存在多个，则选择排序优先级最高的军团
  - 如果不存在可快速加入的军团，则提示当前无快速加入的军团，请手动申请加入军团。

### 创建军团

![图片展示了《FF》游戏创建军团时的界面及编辑旗帜窗口。左侧为创建军团界面，显示旗帜、军团简称、军团誓言等信息，下方有“创建”按钮。右侧是 自动生成图片](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=Zjk1ZTRiNzE4MGJkNWUwMTZmZmZhMmY4ZGMxMzU2MWNfYzg0NjM1N2NhNmZlNGMxNmRjZjhlMzlkYTEwYzY0NjFfSUQ6NzU5NTc5NDY3NzMxNzAxMjQ0NV8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)

- 军团创建信息包括旗帜、军团简称、军团誓言、军团广告、军团申请（是否允许快速加入）、军团条件（等级）
- 编辑旗帜

  - 点击按钮，打开编辑窗口
  - 选择旗帜颜色和旗帜图案，上方展示跟随选择而编号，点击保存，刷新创建联盟旗帜的信息
- 军团简称

  - 只支持1个中文。
  - 超过或不合规不允许输入，并弹出提示
  - 简称编辑成功后，联盟相关成员名称前方显示联盟简称。例：秦·陈刀仔
- 军团名称

  - 最多支持6个字符，只支持中文、英文、数字，不支持标点符号
  - 超过或不合规不允许输入，并弹出提示
- 军团誓言

  - 最多支持20个字符，包括中文、英文、数字、标点符号
  - 超过则不支持再继续输出
- 军团公告

  - 最多支持40个字符，包括中文、英文、数字、标点符号
  - 超过则不支持再继续输出
- 军团申请

  - 点击勾选，勾选允许快速加入，则符合条件的玩家点击加入即可进去，无需军团管理审批
- 入会条件

  - 等级，点击编辑加入军团的最低等级要求
- 创建按钮

  - 按钮上方显示消耗龙晶（当前数量/所需消耗数量）
  
    - 当前数量不足所需消耗数量时，按钮置灰，点击提示龙晶不足
  - 点击创建
  
    - 检测简称、名称是否重名，则弹出提示简称/名称已重名，请重新命名
    - 没有无重名，则消耗龙晶创建成功，生成军团唯一id。关闭界面，提示创建成功，并打开军团主界面

### 军团主界面

- 军团编号：显示军团唯一编号
- 基础信息

  - 包括军团旗帜、名称、简称、等级及经验进度、公告
  - 等级说明icon，点击打开等级说明窗口
  - 编辑按钮，点击打开tips
  
    - 包括编辑军团和解散/退出军团
    - 点击编辑军团，则打开军团编辑界面。该入口只有盟主和管理员才显示，见军团管理-成员权限
    - 会长则显示解散，点击解散，弹出二次确认界面，确认则解散军团。军团成员全部踢出，发送对应邮件给所有成员。
    - 其他成员则显示退出，点击退出，弹出二次确认界面，确认则退出军团。
- 议事厅

  - 显示军团管理角色模型、名称、称号及职位
  - 包括 首领、副首领，数量根据配置决定
  
    - 职位头衔包括军师、大将军、外交官等职位等本版本暂无
  - 职位空则显示剪影状态
- 捐献

  - 点击打开捐献界面
- 功能按钮

  - 管理，点击打开人员管理界面
  - 日常，点击打开日常界面
  - 商店，点击打开商店-公会tab
  - 战功，点击打开战功界面（本版本暂无）
  - 后勤，点击打开后勤界面（本版本暂无）
- 玩法列表

  - 显示公会玩法列表信息，支持向左滑动显示更多
  - 列表包括 军团试炼、世界沙盘、公会分红等，未解锁时显示上锁状态
  - 具体列表信息，见具体的玩法策划案
  
    - 本版本显示军团试炼
    
      - 军团试炼显示图片、名称、次数（今日剩余攻打次数/总次数）
      - 如果免费次数未使用，则显示红点，点击弹出前往提示，确认调用寻路逻辑前往对应NPC
      - 读取对应俱乐部玩法表
    - 其余玩法显示锁定状态，点击提示尚未开放
- 前往军团大厅

  - 点击打开前往军团大厅确认窗口，点击确定，调用回程并寻路前往军团大厅
- 返回

  - 点击关闭界面

### 军团编辑

![图片展示了《FF》游戏中公会详情界面及相关编辑界面。左侧界面显示公会名称“福星银都”，公会等级为1，公会简介、宣言、公告等信息，还设有联盟申请、入会战力条件等选项，底部有“保存”按钮。右侧界面为编辑旗帜界面，可编辑旗帜，下方有多个旗帜图标，底部有“保存编辑”按钮。该图片与文档中“公会详情”部分内容对应，直观呈现了公会信息展示及编辑操作。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YWQwZmZlMTBhYmRlMjk2NjMxOTI3MzM3NzEyODA2MTFfMjZjMTAzMDc2YmM1NGMzYjc4YWEwN2IyZDMyMTcyZDdfSUQ6NzU5NTg0Nzk2NTk4MzQ5MzMxMF8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)

- 同创建军团逻辑，点击保存则保存对应信息编辑

### 军团等级

![图片展示的是游戏中军团等级界面。当前军团等级为1级，成员上限20人，开放功能有公会捐献、商店、讨伐、攻防战。等级2时成员上限为23人，开放功能与1级相同。经验条显示当前经验440，升级经验总值1200。下方文字说明通过公会成员捐献、公会讨伐战斗可提升公会经验。此图与文档中军团等级相关内容对应，直观呈现了军团等级界面的等级、权限及经验等关键信息。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTY5MWY4MWZlZDM4NWNhZGE5ZjIwMjhkNzFiYjkyNDNfZTIwYjZkNzM4ZWM2NjVlODJjY2Q1YjQyNTY1NWE0NTVfSUQ6NzU5NjE4ODUxNjE4NzQ5MTUyOF8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)

- 军团等级升级

  - 军团等级默认从1级开始
  - 玩家参与军团相关玩法会获得军团经验加到军团上
  - 累积经验，则军团升级
  - 新增资源类型：军团经验
- 军团等级权益

  - 根据军团等级表和功能解锁配置决定
  - 权益包括 成员人数上限、军团商店、相关军团功能玩法等
- 军团等级界面

  - 展示当前等级对应拥有的功能权限，包括成员人数上限、开放功能等和下一等级的功能权限
  - 经验条：展示当前经验与升级经验总值
  - 下方显示经验获取方式文本

### 捐献

![图片展示的是《FF》军团系统中捐献界面。界面上方显示“捐献”标题。界面分为基础捐献、高级捐献、尊贵捐献三个部分，每个部分有对应消耗资源（如军团币、军团贡献等）和可捐献次数（均为0/1），并有“捐献”](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=M2IwYmQ2ZTZiYzUxMDdjNmIwMDA0YmNiMTNiOTY1M2ZfYjk5Yjk3OTU1ODk0NjBiOGFlNjMzODllMzY1YTM0N2NfSUQ6NzU5NTg1NzMwMDc5NjQ3NjM4MF8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)

- 分为初级捐献、高级捐献和尊贵捐献

  - 每项捐献奖励、消耗资源、次数，根据读取配置而定
  - 点击捐献，消耗对应资源，并弹出关系获得领取相应奖励
  - 资源不足则按钮置灰，点击提示 资源不足，无法捐献
  - 次数用完则按钮置灰，点击提示 捐献次数已达上限
- 新增资源类型

  - 军团币，用于军团商店的购买物品
  - 军团贡献，用于排名和累积判断奖池发放。需要积累历史贡献和每周贡献（按自然周）
- 红点提醒

  - 基础捐献未捐献时，捐献按钮、公会主界面捐献按钮、公会入口图标按钮、收纳按钮 均显示红点

### 军团管理

![图片展示了《FF》游戏中军团系统的“政务”板块界面。左侧为“成员”界面，显示成员头像、名称、](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZTM1ODVkNmM5YjY2MTExYjA3ODliYmU1NjUzNjUwYzNfMGM0MTlmYTUxYmYzMzQyM2QyZmQ2YzBlOWI1ZjI0MGFfSUQ6NzYwMzYwMDYxMTg5NjAwMzc5OF8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)

- 头部信息

  - 军团旗帜，见上文
  - 等级及对应经验、简称、全称、宣言、公告
  - 说明icon，点击打开等级说明tips
  - 军团编号（点击复制）
  - 编辑按钮，点击打开tips
  
    - 包括编辑军团和解锁/退出军团
    - 点击编辑军团，则打开军团编辑界面。该入口只有盟主和管理员才显示，见军团管理-成员权限
    - 会长则显示解散，点击解散，弹出二次确认界面，确认则解散军团。军团成员全部踢出，发送对应邮件给所有成员。
    - 其他成员则显示退出，点击退出，弹出二次确认界面，确认则退出军团。
- 成员权限

  - 职位包括 盟主和其他管理员（头衔包括 副盟主、军师、大将军、外交官）
  - 盟主权限包括 解散联盟、编辑联盟信息、审批、踢人、设置职位、转让盟主
  - 管理员权限包括 编辑联盟信息、审批、踢人
  - 其他成员无以上权限
- 成员Tab

  - 上方显示军团盟主与管理员头像信息，最多显示5个，超过则滑动
  
    - 信息包括 头像、头像框、名称、职位、等级
  - 成员列表
  
    - 显示军团成员、贡献、在线状态、操作按钮
    - 列表排序
    
      - 根据玩家在线状态排序，距离在线越接近则越靠前
      - 其次根据贡献排序
    - 成员：信息包括头像、头像框、等级、名称、战力、头衔
    
      - 点击头像打开对应玩家信息详情
    - 贡献：显示当周玩家累积贡献
    - 状态：显示玩家最近时间的在线状态，分5段，在线、x小时前、x天前（超过1天）、7天前（超过7天）
    - 操作按钮
    
      - 只有盟主和管理员有此按钮入口和权限
      - 点击拉起操作tips
      - 设置职位：只有盟主才有此按钮和操作权限，点击打开设置职位tips
      
        - tips显示当前管理员职位、职位当前设置人数与职位总人数
        - 默认勾选玩家当前的职位
        - 点击勾选其他职位则将玩家设置为对应职位
        - 如果该职位当前设置人数=职位总人数，则提示“该职位人数已满”
      - 转让盟主：只有盟主才有此按钮和操作权限，点击打开确认窗口，点击确认将盟主转让给该成员
      - 踢出联盟：只有管理员有此按钮和权限，点击打开确认窗口，点击确认踢出联盟
- 日志Tab

  - 显示公会日志，最多保留50条日志
  - 发送日志的内容包括
  
    - 信息+时间（精确到秒）
    
      - Xxx 加入公会
      - Xxx 离开公会
      - Xxx 被xxx 任命为xx职位
      - Xxx 被xxx 逐出公会
- 审核Tab

  - 显示申请成员列表，信息包括成员信息、战力、拒绝/同意
  
    - 列表排序，根据玩家战力降序排序
    - 成员：信息包括头像、头像框、等级、名称
    - 战力：显示玩家最新战力
    - 操作：
    
      - 同意，则玩家加入公会
      - 拒绝，则移除审批列表
      - 注：如果审批玩家已加入其他公会，则将玩家移除列表。
  - 一键同意和一键拒绝：点击一键同意和拒绝列表内全部玩家

### 军团任务

<grid>
<column width-ratio="0.400000">
![图片展示了《FF》游戏中的军团任务界面。界面顶部显示军团进度为30，下方有未领取状态、已领取状态和可领取提示的奖励宝箱。任务列表中，赠送1次体力任务处于未领取状态，消耗50体力任务处于已领取状态，挑战日常副本本次和挑战深渊领主1次任务处于可领取提示状态。任务描述、进度、奖励及前往按钮均有展示，完成任务后可领取奖励，领取后任务刷新为完成状态。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTFhMjI4OTk4NGZhNmU4YjY5YWEyNGIzNzA0OWUxNjFfODBjMmY3Y2RlNDU3NjQwZDNmZWYzMDZiNzkxY2NkY2VfSUQ6NzYwMjQ2MjA1ODgxMDYyNTIyNV8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)
</column>
<column width-ratio="0.600000">
![图片展示的是《FF》游戏中的军团任务界面。界面左侧显示军团进度条，当前进度为30，还有70点可完成。下方有“赠送1次体力”按钮，显示已赠送1次。右侧是任务列表，当前显示“赠送1次体力”任务，进度为1/1，奖励为300体力药剂和1瓶体力药剂，还有前往按钮。该图片与文档中“军团任务”部分内容对应，直观呈现了任务列表中任务的展示样式及奖励情况。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=OWExYmRiZjM4MTI0ZWU1ZTViMDE5YjFjM2QwZjU3YjBfMTQ2M2Y5Mzc2OGE1MmY1MTk2NGIyMTEwODg2ZmJiNGRfSUQ6NzYwMjQ2MjkxNDc2MzQ5MjU2OV8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)
![图片展示的是《FF》游戏中“参与公会捐献3次”的任务奖励界面。左侧有三个图标，分别代表 自动生成](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=NzZmNWVhMWY5NzczYmUxMTczYjAxZDFkOGE3YTc0M2NfMjFlMDc4MjRjZGNlNzU1NTgzZmI4MTNhMjBiYzI0ZDJfSUQ6NzYwMjQ2Mzg2ODkwMzgzNjYyOF8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)
</column>
</grid>

1. 信息包括 军团进度、任务列表
2. 军团进度

   1. 军团所有成员完成会增加进度，累积进度，全员均可领取奖励
   
      1. 未完成任务或当天加入也可领取奖励
      2. 每日限领1次/任务也只能完成一次，换公会不可再领取完成同一id的
   2. 左侧显示完成活跃度统计，右侧展示进度值及奖励宝箱
   
      1. 统计全军团
      2. 奖励宝箱分为 未领取状态、已领取状态和可领取红点提示
      3. 点击宝箱，展示奖励预览tips
   3. 军团进度每日0点重置刷新，同时刷新任务列表任务
3. 任务列表

   1. 展示任务描述、进度、奖励、前往按钮
   2. 当任务完成时，按钮变为领取按钮，点击弹出恭喜获得，领取奖励
   3. 领取奖励后，任务刷新为完成状态
   4. 注：如果玩家切换军团，之前的进度依旧加在原军团，之后的任务进度加在新军团

### 军团商店

- 见<cite doc-id="FYqJd0eEAo3Uxxx3dc0cEDY5nLc" file-type="docx" title="【FF】商店系统" type="doc"></cite>
- 新增条件枚举 归属军团等级大于等于，用于商店物品的购买权限

### 特殊逻辑

- 会长自动转让逻辑

  - 当会长超过48小时未登录后，公会会长自动转让给战力最高且24小时内在线的玩家
- 当玩家加入工会后，玩家名称需要展示简称。例：【汉】陈刀仔
- 军团

  - 加入军团后，解锁军团内部聊天房间
  - 只限用一军团的人才可开放

  ![图片展示的是游戏聊天界面，左侧有“世界”“公会”“私聊”“系统”四个选项卡，其中“公会”选项卡被黄色框线突出显示。右侧是聊天窗口，显示了玩家“达恩·星霜”在“开发环境2服”下的聊天记录，有“达恩·星霜”和“AUV”等玩家的聊天内容](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=YTk3MTFhYjdiY2EwNzE4M2I5NGI0MzY5OTQ3NDk5MjRfY2Q0NThiZTRjYTNiMGQ2NDljMGY2NDUyNzczMTc2MzZfSUQ6NzYxNjIwMDA0OTE0Nzc0MzE2MV8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)
- 玩家军团

  - 加入军团后，需要在玩家个人信息，其他玩家信息两个界面显示玩家对应公会

<grid>
<column width-ratio="0.497719">
![图片展示的是《FF》游戏中玩家个人信息界面。界面上方显示玩家等级为59，称号为“暂无称号”，并有账号ID、职业、公会等信息。下方是玩家的属性，包括攻击、防御、生命值等，以及装备和技能图标。右上角有“拉黑”和“举报”按钮，右下角有“加好友”按钮。该界面与文档中“玩家军团”部分上下文对应，展示了加入军团后，玩家个人信息界面显示对应公会的功能设计。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ZTMyYTBiNzZhY2I4YmQzYjk0ZDk5OTAxN2U0NDMzNzZfZWRiYzEzYTg4MGM1YWUwODEzOWNiNjE2YmIwN2M2MWZfSUQ6NzYxNjE5OTc4NzI4MDc2Mzg0N18xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)
</column>
<column width-ratio="0.502281">
![图片展示的是游戏中的个人信息界面。界面上方有“个人信息”标题，右上角有“X”关闭按钮。中间部分显示角色头像、等级（Lv.40）和经验（0%），下方是角色信息，包括名字、账号、职业、公会、服务器等。左下角有角色等级图标和等级（1,003）。底部有“角色”和“设置”两个选项卡。该界面与文档中“玩家军团”部分上下文对应，用于显示玩家对应公会信息。](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/authcode/?code=ODVjMGIxYmMyYWMyYzhlYTk0YTczMWY2YzZkODY3YWRfODE1NDEyYzQ2ZjMxOGUwOTZiMjY5OWY3YzAwYmIzNGZfSUQ6NzYxNjE5OTgyMTQ0MzYzMjMzMV8xNzgzNTAwNjQ3OjE3ODM1MDQyNDdfVjM)
</column>
</grid>

### 公会场景

- 进入权限

  - 同军团成员才可进入同一军团场景
  - 玩家被离开军团后，如果此时处于军团场景中，弹出确认提示并自动返回主城
- 进入方式

  - 接触公会场景碰撞盒，播放转场动画进入军团场景
  - 如果玩家此时无军团，则在当前场景弹出加入军团窗口
- 公会场景UI

  - 同主城场景
