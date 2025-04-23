# 微信扫码点名系统 - 数据库设计文档

**小组成员:** 
* 洪家权
* 盖烈森
* 马静
* 陈皓阳

### 1. 引言与项目概述

随着信息技术在教育领域的广泛应用，传统的人工点名方式在效率、准确性和数据管理方面日益显现出不足。在高校中，对大规模课程进行快速、准确、便捷的考勤管理成为了迫切的需求。本项目——“微信扫码点名系统”——旨在构建一套自动化的考勤管理解决方案。

本系统利用微信平台的用户基础，及其扫码接口作为前端签到入口；核心数据，包括学生、课程、教师、考勤及请假记录等，将由后端应用程序依赖健壮的关系数据库进行高效、安全的存储与管理；同时，系统提供 Web 前端界面，支持各类用户（学生、教师、管理员）进行信息查询、管理操作（增删改）等交互，并能直观地展示所需的考勤统计结果。通过整合这些技术，期望能显著提升考勤效率，减少人为错误，并为教学管理提供有效的数据支持。

本文档作为该系统数据库设计的详细说明，将遵循数据库设计的基本原则与规范，从概念模型（E-R图、实体、关系）到逻辑与物理模型（表结构、数据类型、约束条件、范式分析），全面阐述数据库的设计思路、结构和具体实现细节，为后续的系统开发和数据库建立提供清晰的蓝图和依据。



### 2. 需求分析概要

本系统围绕学生、教师和管理员三类用户的交互展开，满足他们在考勤、教学、管理等方面的核心需求，并需要对相关的核心数据进行有效管理。


#### 2.1 数据流图

![数据流图](数据流图.png)

#### 2.2 用户角色及核心功能

* **学生 (Student):**
    * **扫码签到:** 在教师发起的考勤事件有效时间内，使用微信扫描指定二维码完成签到。
    * **请假申请:** 针对特定的考勤事件，在线提交请假申请及理由。
    * **信息查询:** 查看个人基本信息、选课列表、课程表（上课时间、地点）、历史考勤记录以及请假申请的审批状态。
    * **选课操作:** [可能功能] 执行选课、退课操作（具体流程根据系统实现，可能由管理员直接处理）。

* **教师 (Teacher):**
    * **发起与管理考勤:** 为所授课程创建（发起）考勤事件，设置有效扫码时间窗口，系统据此生成二维码（以事件ID为内容）供展示。可将考勤事件设为有效或无效状态。
    * **查看考勤结果:** 实时或事后查看指定考勤事件的学生签到详情（出勤、缺勤、请假名单及时间）。
    * **请假审批:** 审核名下学生提交的请假申请，进行批准或驳回操作，并可添加备注。
    * **信息查询:** 查看个人基本信息、所授课程列表及详细的课程时间安排。

* **管理员 (Admin):**
    * **基础信息管理:** 在后台管理系统维护院系、专业、学生、教师、课程等基础信息（执行增、删、改操作）。
    * **教学安排管理:** 管理教师的教学任务分配（TeachingAssignment）以及具体的课程时间安排（ClassSchedule）。
    * **选课管理:** 在后台直接处理学生的选课记录（Enrollment），包括添加、删除（处理中途选/退课）。
    * **数据监控与统计:** 查询、浏览院系或课程范围内的考勤数据统计结果（如出勤率、缺勤名单等，由系统根据原始考勤记录动态生成报表或视图）。
    * **[可能功能] 系统设置:** 配置系统级参数（例如默认的考勤有效时长等）。

#### 2.3 主要数据需求

为实现上述功能，数据库需要存储和管理以下核心信息：

* **组织与人员:** 院系 (Department)、专业 (Major)、学生 (Student)、教师 (Teacher)、管理员 (Admin) 的基本信息。
* **课程与教学:** 课程 (Course) 的基本信息、教师与课程之间的教学安排 (TeachingAssignment)、该安排下的具体上课时间表 (ClassSchedule)。
* **学生与课程关系:** 学生选修课程的记录 (Enrollment)，包含学期信息。
* **考勤核心流程:**
    * 特定日期为某课程发起的考勤事件 (AttendanceEvent)，包含有效时间窗口和状态。
    * 学生针对某次考勤事件的最终考勤记录 (Attendance)，包含状态和扫码时间（如果出勤）。
    * 学生针对某次考勤事件提交的请假申请 (LeaveRequest)，包含原因、提交时间和审批信息（如果实现）。


### 3. 概念模型设计 (Conceptual Model Design)

#### 3.1 E-R 图 (Entity-Relationship Diagram)

![ER图](ER图.png)

#### 3.2 经规范化的实体列表 (Entity List)

1.  **院系 (Department):** 院系ID (PK), 院系名
2.  **专业 (Major):** 专业ID (PK), 专业名, 所属院系ID (FK)
3.  **学生 (Student):** 学生学号 (PK), 学生姓名, 学生性别, 学生专业ID (FK)
4.  **课程 (Course):** 课程代码 (PK), 课程名称, 开课院系ID (FK)
5.  **教师 (Teacher):** 教师工号 (PK), 教师姓名, 所属院系ID (FK)
6.  **选课记录 (Enrollment):** 选课记录ID (PK), 学生学号 (FK), 课程代码 (FK), 选课学期
7.  **考勤记录 (Attendance):** 考勤记录ID (PK), 选课记录ID (FK), 考勤事件ID (FK), 扫码考勤时间, 考勤状态
8.  **请假申请 (LeaveRequest):** 请假申请ID (PK), 选课记录ID (FK), 考勤事件ID (FK), 请假内容, 提交时间, 审批状态, 审批备注, 审批教师工号 (FK)
9.  **考勤事件 (AttendanceEvent):** 考勤事件ID (PK), 课程代码 (FK), 扫码有效开始时间, 扫码有效结束时间, 事件日期, 事件状态
10. **管理员 (Admin):** 管理员ID (PK), 管理员姓名
11. **教学安排 (TeachingAssignment):** 教学安排ID (PK), 教师工号 (FK), 课程代码 (FK)
12. **课程时间安排 (ClassSchedule):** 时间安排ID (PK), 教学安排ID (FK), 星期几, 开始节次, 结束节次, 上课地点


#### 3.3 关系描述 (Relationship Descriptions)

1.  设立 (院系 1:N 专业)
2.  属于 (专业 1:N 学生)
3.  属于 (院系 1:N 教师)
4.  开设 (院系 1:N 课程)
5.  选课 (学生 1:N 选课记录)
6.  被选课 (课程 1:N 选课记录)
7.  产生 (选课记录 1:N 考勤记录)
8.  产生 (选课记录 1:N 请假申请)
9.  产生 (课程 1:N 考勤事件)
10. 属于 (考勤事件 1:N 考勤记录)
11. 产生 (课程 1:N 教学安排)
12. 授课 (教师 1:N 教学安排)
13. 属于 (教学安排 1:N 课程时间安排)
14. 教学安排 (课程 N:M 教师) 
    *注：通过实体 11 教学安排 实现*


### 4. 数据库逻辑/物理设计 (Logical/Physical Design)

#### 4.1 表结构定义 (Table Definitions)

```sql
-- 创建数据库
CREATE DATABASE `wx_attendance_db` 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- 实体1: Department (院系信息)
CREATE TABLE `Department` (
  `dept_id` tinyint unsigned NOT NULL AUTO_INCREMENT COMMENT '院系ID',
  `dept_name` varchar(50) NOT NULL COMMENT '院系名',
  PRIMARY KEY (`dept_id`),
  UNIQUE KEY `uk_dept_name` (`dept_name`)
) ENGINE=InnoDB COMMENT='院系信息表';

-- 实体2: Major (专业信息)
CREATE TABLE `Major` (
  `major_id` tinyint unsigned NOT NULL AUTO_INCREMENT COMMENT '专业ID',
  `major_name` varchar(50) NOT NULL COMMENT '专业名',
  `dept_id` tinyint unsigned NOT NULL COMMENT '所属院系ID',
  PRIMARY KEY (`major_id`),
  UNIQUE KEY `uk_major_name` (`major_name`),
  KEY `fk_major_dept` (`dept_id`),
  CONSTRAINT `fk_major_dept` 
    FOREIGN KEY (`dept_id`) REFERENCES `Department` (`dept_id`) 
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='专业信息表';

-- 实体3: Student (学生信息)
CREATE TABLE `Student` (
  `stu_id` char(11) NOT NULL COMMENT '学生学号',
  `stu_name` varchar(50) NOT NULL COMMENT '学生姓名',
  `stu_sex` enum('男','女') NOT NULL COMMENT '学生性别',
  `major_id` tinyint unsigned DEFAULT NULL COMMENT '学生专业ID',
  PRIMARY KEY (`stu_id`),
  KEY `fk_student_major` (`major_id`),
  CONSTRAINT `fk_student_major` 
    FOREIGN KEY (`major_id`) REFERENCES `Major` (`major_id`) 
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='学生信息表';

-- 实体4: Course (课程信息)
CREATE TABLE `Course` (
  `course_id` char(12) NOT NULL COMMENT '课程代码',
  `course_name` varchar(50) NOT NULL COMMENT '课程名称',
  `dept_id` tinyint unsigned NOT NULL COMMENT '开课院系ID',
  PRIMARY KEY (`course_id`),
  KEY `fk_course_dept` (`dept_id`),
  CONSTRAINT `fk_course_dept` 
    FOREIGN KEY (`dept_id`) REFERENCES `Department` (`dept_id`) 
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='课程信息表';

-- 实体5: Teacher (教师信息)
CREATE TABLE `Teacher` (
  `teacher_id` char(5) NOT NULL COMMENT '教师工号',
  `teacher_name` varchar(50) NOT NULL COMMENT '教师姓名',
  `dept_id` tinyint unsigned NOT NULL COMMENT '所属院系ID',
  PRIMARY KEY (`teacher_id`),
  KEY `fk_teacher_dept` (`dept_id`),
  CONSTRAINT `fk_teacher_dept` 
    FOREIGN KEY (`dept_id`) REFERENCES `Department` (`dept_id`) 
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='教师信息表';

-- 实体6: Enrollment (选课记录)
CREATE TABLE `Enrollment` (
  `enroll_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '选课记录ID',
  `stu_id` char(11) NOT NULL COMMENT '学生学号',
  `course_id` char(12) NOT NULL COMMENT '课程代码',
  `semester` char(6) NOT NULL COMMENT '选课学期',
  PRIMARY KEY (`enroll_id`),
  UNIQUE KEY `uk_enroll_stu_course_sem` (`stu_id`,`course_id`,`semester`),
  KEY `fk_enroll_course` (`course_id`),
  CONSTRAINT `fk_enroll_student` 
    FOREIGN KEY (`stu_id`) REFERENCES `Student` (`stu_id`) 
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_enroll_course` 
    FOREIGN KEY (`course_id`) REFERENCES `Course` (`course_id`) 
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='选课记录表';

-- 实体9: AttendanceEvent (课堂考勤事件)
CREATE TABLE `AttendanceEvent` (
  `event_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '考勤事件ID',
  `course_id` char(12) NOT NULL COMMENT '课程代码',
  `event_date` date NOT NULL COMMENT '事件日期',
  `scan_start_time` time NOT NULL COMMENT '扫码有效开始时间',
  `scan_end_time` time NOT NULL COMMENT '扫码有效结束时间',
  `event_status` enum('有效','无效') NOT NULL DEFAULT '有效' COMMENT '事件状态',
  `creation_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '考勤事件创建时间',
  PRIMARY KEY (`event_id`),
  KEY `fk_event_course` (`course_id`),
  CONSTRAINT `fk_event_course` 
    FOREIGN KEY (`course_id`) REFERENCES `Course` (`course_id`) 
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='课堂考勤事件表';

-- 实体7: Attendance (考勤记录)
CREATE TABLE `Attendance` (
  `attend_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '考勤记录ID',
  `enroll_id` int unsigned NOT NULL COMMENT '选课记录ID',
  `event_id` int unsigned NOT NULL COMMENT '考勤事件ID',
  `scan_time` datetime DEFAULT NULL COMMENT '扫码考勤时间',
  `status` enum('出勤','缺勤','请假') NOT NULL COMMENT '考勤状态',
  `notes` text COMMENT '备注',
  PRIMARY KEY (`attend_id`),
  UNIQUE KEY `uk_attend_enroll_event` (`enroll_id`,`event_id`),
  KEY `fk_attend_event` (`event_id`),
  CONSTRAINT `fk_attend_enroll` 
    FOREIGN KEY (`enroll_id`) REFERENCES `Enrollment` (`enroll_id`) 
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_attend_event` 
    FOREIGN KEY (`event_id`) REFERENCES `AttendanceEvent` (`event_id`) 
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='学生考勤记录表';

-- 实体8: LeaveRequest (请假申请)
CREATE TABLE `LeaveRequest` (
  `leave_request_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '请假申请ID',
  `enroll_id` int unsigned NOT NULL COMMENT '选课记录ID',
  `event_id` int unsigned NOT NULL COMMENT '考勤事件ID',
  `reason` text NOT NULL COMMENT '请假内容',
  `submit_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
  `approval_status` enum('待审批','已批准','已驳回') NOT NULL DEFAULT '待审批' COMMENT '审批状态',
  `approver_teacher_id` char(5) DEFAULT NULL COMMENT '审批教师工号',
  `approval_timestamp` datetime DEFAULT NULL COMMENT '审批时间',
  `approver_notes` text COMMENT '审批备注',
  PRIMARY KEY (`leave_request_id`),
  UNIQUE KEY `uk_leave_enroll_event` (`enroll_id`,`event_id`),
  KEY `fk_leave_event` (`event_id`),
  KEY `fk_leave_approver` (`approver_teacher_id`),
  CONSTRAINT `fk_leave_enroll` 
    FOREIGN KEY (`enroll_id`) REFERENCES `Enrollment` (`enroll_id`) 
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_leave_event` 
    FOREIGN KEY (`event_id`) REFERENCES `AttendanceEvent` (`event_id`) 
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_leave_approver` 
    FOREIGN KEY (`approver_teacher_id`) REFERENCES `Teacher` (`teacher_id`) 
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='请假申请表';

-- 实体10: Admin (管理员)
CREATE TABLE `Admin` (
  `admin_id` char(5) NOT NULL COMMENT '管理员ID',
  `admin_name` varchar(50) NOT NULL COMMENT '管理员姓名',
  PRIMARY KEY (`admin_id`)
) ENGINE=InnoDB COMMENT='管理员信息表';

-- 实体11: TeachingAssignment (教学安排)
CREATE TABLE `TeachingAssignment` (
  `assign_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '教学安排ID',
  `teacher_id` char(5) NOT NULL COMMENT '教师工号',
  `course_id` char(12) NOT NULL COMMENT '课程代码',
  PRIMARY KEY (`assign_id`),
  UNIQUE KEY `uk_teach_assign_teacher_course` (`teacher_id`,`course_id`),
  KEY `fk_teach_assign_course` (`course_id`),
  CONSTRAINT `fk_teach_assign_teacher` 
    FOREIGN KEY (`teacher_id`) REFERENCES `Teacher` (`teacher_id`) 
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_teach_assign_course` 
    FOREIGN KEY (`course_id`) REFERENCES `Course` (`course_id`) 
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB COMMENT='教学安排表 (Teacher M:N Course)';

-- 实体12: ClassSchedule (课程时间安排)
CREATE TABLE `ClassSchedule` (
  `schedule_id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '时间安排ID',
  `assign_id` int unsigned NOT NULL COMMENT '教学安排ID',
  `day_of_week` tinyint unsigned NOT NULL COMMENT '星期几',
  `start_period` tinyint unsigned NOT NULL COMMENT '开始节次',
  `end_period` tinyint unsigned NOT NULL COMMENT '结束节次',
  `location` varchar(50) DEFAULT NULL COMMENT '上课地点',
  PRIMARY KEY (`schedule_id`),
  KEY `fk_schedule_assign` (`assign_id`),
  CONSTRAINT `fk_schedule_assign` 
    FOREIGN KEY (`assign_id`) REFERENCES `TeachingAssignment` (`assign_id`) 
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_day_of_week` 
    CHECK (((`day_of_week` >= 1) and (`day_of_week` <= 7))),
  CONSTRAINT `chk_start_period` 
    CHECK (((`start_period` > 0) and (`start_period` <= 13))),
  CONSTRAINT `chk_end_period` 
    CHECK (((`end_period` >= `start_period`) and (`end_period` <= 13)))
) ENGINE=InnoDB COMMENT='课程时间安排表';
```


#### 4.2 范式分析 (Normalization Analysis)

通过合理的实体划分和关系设计，本数据库模式达到了第三范式 (3NF)，有助于减少数据冗余，避免插入、删除和更新操作中的异常情况，保证了数据的一致性，为上层应用程序提供了一个稳定、可靠的数据基础。

1.  **符合第一范式 (1NF):** **原子性**

数据库中的所有表都设计为关系模式，每个属性都存储原子性的数据，不存在重复组或多值属性存储在单一单元格内的情况。例如，课程时间安排被分解到 `ClassSchedule` 表中，确保了星期几、开始节次、结束节次等信息的原子性存储。


2.  **符合第二范式 (2NF):** **非主键属性完全依赖于主键**
  
对于所有使用 **单列主键** 的表（如 `Department`, `Major`, `Student`, `Course`, `Teacher`, `Admin`, `Enrollment`, `AttendanceEvent`, `Attendance`, `LeaveRequest`, `TeachingAssignment`, `ClassSchedule`），其所有非主键属性都直接依赖于这个唯一的主键，不存在部分依赖于主键组合的情况，因此自动满足 2NF。
 
 对于通过 **复合主键** 来保证业务逻辑唯一性的表（如 `Enrollment` 的 `(stu_id, course_id, semester)` 组合；`Attendance` 和 `LeaveRequest` 的 `(enroll_id, event_id)` 组合；`TeachingAssignment` 的 `(teacher_id, course_id)` 组合），其非主键属性（如 `Enrollment.semester`, `Attendance.status`, `LeaveRequest.reason` 等）也依赖于这个能唯一确定一行记录的组合主键，而非仅依赖于组合键的一部分。


3. **符合第三范式 (3NF):** **避免了非主键属性对主键的传递依赖**

在 `Student` 表的设计中，只存储了外键 `major_id`。学生所属的院系信息 (`dept_id` 或 `dept_name`) 需要通过 `Student.major_id` 关联到 `Major` 表，再通过 `Major.dept_id` 关联到 `Department` 表来获得，这就消除了 `stu_id -> major_id -> dept_id` 这样的传递依赖关系。

类似地，`Course`只存储了开课院系的 `dept_id`，`Teacher`只存储了所属院系的 `dept_id`，都避免了相关的传递依赖。`AttendanceEvent` (考勤事件) 只存储了 `course_id`，与课程相关的其他信息（如课程名、开课院系）需通过关联 `Course` 表获得。



#### 4.3 完整性约束说明 (Integrity Constraint Explanation)

为了确保数据库中数据的准确性、一致性、有效性和业务规则的遵循，本设计在物理模式中定义了多种完整性约束。主要体现在以下几个方面：


**实体完整性 (Entity Integrity):**

* 每一个表都定义了主键

* 主键列被数据库系统强制要求具有 唯一性 和 非空性 

* 根据实体特性，混合使用了自增整数（如 `enroll_id`, `event_id`）作为代理主键和具有业务含义的定长字符（如 `stu_id`, `course_id`, `teacher_id`）作为自然主键


**参照完整性 (Referential Integrity):**

* 广泛使用 外键约束 来定义和强制表间的引用关系

* 根据业务逻辑为外键设置了不同的 删除 和 更新 规则

* **`ON DELETE RESTRICT`**:应用于基础数据表的主键被引用时，其核心作用是，只有当没有任何其他记录再引用这条基础数据记录时，才允许将其删除。例如，对于 `dept_id = 1`，必须先将 `Major`、`Teacher`、`Course` 表中所有 `dept_id = 1` 的记录全部删除，或者将它们的 `dept_id` 修改为引用其他有效的院系 ID 之后，才能成功删除该条记录

* **`ON DELETE CASCADE`**: 应用于关联/从属关系（如 `Enrollment`, `Attendance`, `LeaveRequest`, `TeachingAssignment`, `ClassSchedule`, `AttendanceEvent`）。当主记录（如 `Student`, `Course`, `TeachingAssignment`, `AttendanceEvent`, `Enrollment`）被删除时，相关的从属记录（选课记录、考勤记录、请假记录、时间安排等）也会被自动级联删除，避免产生无意义的孤立数据

* **`ON DELETE SET NULL`**: 应用于允许关联丢失但记录本身仍有意义的情况，如 `Student.major_id` 和 `LeaveRequest.approver_teacher_id`。当对应的专业或审批教师被删除时，学生记录或请假申请记录仍然保留，只是对应的外键字段被置为 `NULL`

* **`ON UPDATE CASCADE`**: 普遍应用于所有外键。当被引用的主键值发生更新时，所有引用该键的外键值也会自动更新，保持引用关系不断裂


**域完整性 (Domain Integrity):**

* 确保单个列中的数据值是有效的，符  合其预定义的类型、格式、范围或集合。

* **数据类型** 为每个字段选择了精确的数据类型，如 `TINYINT UNSIGNED`, `CHAR(11)`, `VARCHAR(50)`, `DATE`, `TIME`, `DATETIME`, `TEXT`, `TIMESTAMP`

* **非空约束** 对业务逻辑上必须存在的字段（如名称、ID、部分状态、日期等）强制要求非空

* **枚举类型** 用于精确限定取值范围的字段，如 `stu_sex` ('男', '女')，`Attendance.status` ('出勤', '缺勤', '请假')，`LeaveRequest.approval_status` ('待审批', '已批准', '已驳回')，`AttendanceEvent.event_status` ('有效', '无效')。

* **检查约束** 在 `ClassSchedule` 表中使用了 `CHECK` 约束来确保 `day_of_week` (1-7) 和 `start_period`/`end_period` (1-13 且结束不早于开始) 的值在逻辑上有效

* **默认值** 为某些字段（如 `LeaveRequest.submit_time`, `AttendanceEvent.creation_time`, `LeaveRequest.approval_status`, `AttendanceEvent.event_status`）设置了默认值，简化插入操作并提供初始状态


**用户定义完整性 (User-Defined Integrity):**


* **唯一约束** 除了主键外，还需保证业务唯一性的字段或字段组合（如 `dept_name`, `major_name`, `Enrollment` 表的 `(stu_id, course_id, semester)` 等组合添加了唯一约束，这些约束确保了关键规则（如学生不能重复选同一学期的课，一次考勤事件对一个学生只有一条考勤或请假记录）

* **应用逻辑:** 更复杂的业务规则，例如“学生不能在考勤事件结束后提交请假申请”或“只有状态为‘有效’的考勤事件才能接受签到”，通常在应用程序层面（后端代码）进行检查和强制实施，作为数据库约束的补充



### 5. 核心 SQL 查询示例

#### 5.1 学生

##### 1.


#### 5.2 教师

##### 1.



#### 5.3 管理员

##### 1.