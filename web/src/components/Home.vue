<template>
  <div id="app">
    <h1>{{module}}</h1>
    <div id="toolbar">
      <!-- 导出按钮 -->
      <el-button type="primary" @click="downloadFile">导出</el-button>
      <!-- 切换模式，使用v-if来和moudle的状态绑定 -->
      <el-button v-if="module == '分类模式'" type="primary" @click="changeToOCR">切换到OCR模式</el-button>
      <el-button v-if="module == 'OCR模式'" type="primary" @click="changeToClassify">切换到分类模式</el-button>
      <!-- 开始分类按钮 -->
      <el-button type="success" @click="startClassification">开始调试</el-button>

      <!-- 设置项按钮 -->
      <el-button type="info"  @click="openSettingsDialog">
        正式任务
      </el-button>
    <!-- 打开任务状态弹窗按钮 -->
    <el-button @click="openTaskStatusDialog">查看任务状态</el-button>


    <!-- 任务状态弹窗 -->
    <!-- 任务状态弹窗 -->
    <el-dialog title="任务状态" v-model="taskStatusDialogVisible" width="50%">
      <div style="margin-bottom: 20px;">
        <el-input
          v-model="searchTaskId"
          placeholder="输入任务ID进行检索"
          style="width: 70%; margin-right: 10px;"
        ></el-input>
        <el-button type="primary" @click="fetchTasks">检索</el-button>
      </div>
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="task_id" label="任务ID" width="180"></el-table-column>
        <el-table-column label="进度">
      <template #default="scope">
        <el-progress :percentage="Math.round(scope.row.progress * 100)" />
      </template>
    </el-table-column>
        <el-table-column prop="status" label="状态"></el-table-column>
        <el-table-column prop="task_type" label="任务类型"></el-table-column>
          <!-- 新增下载列 -->
  <el-table-column label="操作" width="120">
    <template #default="scope">
      <el-button
        type="success"
        size="small"
        :disabled="scope.row.status !== '已完成'"
        @click="handleDownload(scope.row.task_id)"
      >
        下载
      </el-button>
    </template>
  </el-table-column>
      </el-table>

      <span slot="footer" class="dialog-footer">
        <el-button @click="taskStatusDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>



      <h1>设置项</h1>
      <!-- 设置项表单 -->
      <el-form :model="settings" ref="settingsForm">
        <el-form-item label="每批数据量" :rules="[{ required: true, message: '请输入每批数据量', trigger: 'blur' }]">
          <el-input-number v-model="settings.limit" :min="1" label="每批数据量"></el-input-number>
        </el-form-item>

        <el-form-item v-if="module == '分类模式'" label="分类数量" :rules="[{ required: true, message: '请输入分类数量', trigger: 'blur' }]">
          <el-input-number v-model="settings.classifyNum" :min="1" label="分类数量"></el-input-number>
        </el-form-item>

        <el-form-item v-if="module == '分类模式'" label="分类标签名" :rules="[{ required: true, message: '请输入分类标签名', trigger: 'blur' }]">
          <el-input v-model="settings.classifyContent" placeholder="请输入分类标签，用逗号分隔"></el-input>
        </el-form-item>

        <el-form-item v-if="module == '分类模式'" label="角色">
        <el-input type="textarea" 
                v-model="settings.classifyRole" 
                rows="3" 
                placeholder="请输入分类角色"></el-input>
      </el-form-item>

      <el-form-item v-if="module == '分类模式'" label="目标">
        <el-input type="textarea"
                v-model="settings.classifyGoal"
                rows="5"
                placeholder="请输入分类目标"></el-input>
      </el-form-item>

      <el-form-item v-if="module == '分类模式'" label="评分标准">
        <el-input type="textarea"
                v-model="settings.scoringCriteria"
                rows="5"
                placeholder="请输入评分标准"></el-input>
      </el-form-item>

      <el-form-item v-if="module == '分类模式'" label="重要提示">
        <el-input type="textarea"
                v-model="settings.importantNotes"
                rows="5"
                placeholder="请输入重要提示"></el-input>
      </el-form-item>
      <el-form-item v-if="module == '分类模式'" label="完整分类要求">
      <el-input type="textarea"
              :value="classifyRequirement"
              rows="10"
              readonly></el-input>
    </el-form-item>
      </el-form>
      <!-- 提示信息 -->
      <div class="tips-container">
        <el-tooltip content="请在A1单元格设置要分类的文本内容，在B1及以后的单元格设置要分类的标签。有 A1必须为'content'。" placement="right">
          <i class="el-icon-info info-icon"></i>
        </el-tooltip>
        <el-tag v-show="module == '分类模式'" type="success">提示：A列为数据源，B列之后为分类的结果  然后从A2开始填充要查询的数据</el-tag>
        <el-tag v-show="module == 'OCR模式'" type="success">提示：A列为图片的URL地址，B列为OCR识别的结果</el-tag>
      </div>
    </div>
    <hr/>
    <el-progress v-if="showProgress" :percentage="progressPercentage" :text-inside="true"       :stroke-width="15"
      status="success"
      striped
      striped-flow></el-progress>
    <h1>在线调试</h1>
    <!-- 表格容器 -->
    <div id="grid-container" style="width: 100%; height: 500px;"></div>

    <!-- 设置弹窗 -->
    <el-dialog title="正式任务" v-model="settingsDialogVisible" width="40%">
      <el-form ref="formRef" :model="form" label-width="120px">
        <!-- 文件上传 -->
        <el-form-item label="上传文件">
          <el-upload
            ref="uploadRef"
            :before-upload="beforeUpload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :auto-upload="false"
            @change="handleFileChange"
            accept=".xlsx"
          >
            <el-button type="primary">选择文件</el-button>
            <div slot="tip" class="el-upload__tip">仅支持 .xlsx 文件</div>
          </el-upload>
        </el-form-item>
        <!-- 任务类型选择 -->
        <el-form-item label="任务类型">
          <el-radio-group v-model="form.taskType">
            <el-radio label="OCR任务">OCR任务</el-radio>
            <el-radio label="分类任务">分类任务</el-radio>
          </el-radio-group>
        </el-form-item>
        <!-- 按钮 -->
        <el-form-item>
          <el-button type="primary" @click="createTask">创建任务</el-button>
          <el-button @click="cancelTask">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script>
import { ElButton, ElTooltip, ElTag, ElNotification, ElDialog, ElForm, ElFormItem, ElInput, ElInputNumber } from 'element-plus';
import 'element-plus/dist/index.css';
import axios from 'axios';
import x_spreadsheet from "x-data-spreadsheet";
import * as XLSX from 'xlsx';
import "x-data-spreadsheet/dist/xspreadsheet.css";
import { Delete, Edit, Search, Share, Upload, Setting} from '@element-plus/icons-vue'
export default {
  name: 'Home',
  components: {
    ElButton,
    ElTooltip,
    ElTag,
    ElNotification,
    ElDialog,
    ElForm,
    ElFormItem,
    ElInput,
    ElInputNumber,
  },
  data() {
    return {
    grid: null,
    taskStatusDialogVisible: false,
    tasks: [],
    filteredTasks: [],
    searchTaskId: '',
    form : {
              file: null,
              taskType: 'OCR任务', // 默认选择OCR任务
            },

    selectedFile: null,
    formRef : null,
    uploadRef : null,
      settingsDialogVisible: false,  // 控制设置弹窗的显示与隐藏
      module: '分类模式',
      showProgress: false,

      progressPercentage: 0,
      settings: {
        limit: 20,  // 默认每批数据量
        classifyNum: 2,  // 默认分类数量
        classifyContent: '风险倾向,收益预期',  // 默认分类标签
        classifyRole: '你是一位专业的金融行为分析师。请仔细分析以下投资者的社交媒体发言，判断该发言是否表现出投资者倾向于追求高风险-高回报的"彩票式股票"投资特征。',  // 默认分类角色
        classifyGoal: ` 请逐步分析以下要素：
        1. 风险认知指标：
        * 发言是否显示出高风险承受意愿（如，"赌"、"无所谓风险"）
        * 是否提及"破釜沉舟"式投资决策（如，"生死一搏"、"不成功便成仁"）
        * 是否表现出"全部押注"倾向（如，"孤注一掷"、"全仓买入"、"一把梭哈"）
        * 是否体现非理性乐观（如，忽略风险，仅提到收益）
        * 是否偏好高波动性股票或偏好跟风炒作（如，提到"妖股"、"大起大落"，或提到"大家都在买"、"热点"）
        2. 收益预期指标：
        * 是否期待极高收益回报（如，提及"翻倍"、"一夜暴富"、“涨停”）
        * 是否有不切实际的收益预期（如，对短期回报持有过度乐观预期）
        * 是否频繁提及"暴富"概念（如，"暴利"、"财富自由"）
        * 是否过分强调短期收益（如，"明天就能赚"、"短期暴涨"）
        * 是否表现出急于求成心态（如，提到"急于翻身"、"抓住最后机会"）`,  // 默认分类目标
        scoringCriteria: `      量化评分维度
        请分别对以下维度进行0-1分的评分：
        - 风险倾向：[0-分]1（1分表示风险规避，1分表示极度风险追求）
        - 收益预期：[0-1分]（1分表示理性预期，1分表示极度非理性预期）
        - 若无法根据文本识别出上述某一维度，则该维度赋值为'null'`,  // 默认评分标准
        importantNotes: `   关键词识别
        请特别关注以下类型词汇的出现：
        赌博类：梭哈、豪赌、赌一把、孤注一掷、下注、中奖、彩票
        暴利类：暴富、翻倍、一夜暴富、翻身、财富自由、风口、黑马、独角兽、涨停
        极端类：破釜沉舟、生死一搏、破罐破摔、刀口舔血、放手一搏、富贵险中求
        机会类：抄底、抓住机会、押宝
        网络俚语：一波肥、吃鸡、躺赢、单车变摩托
        **重要提示**
        1. 避免过度推断，分析应基于文本明确表达。
        2. 注意区分正常投资讨论和彩票式投资倾向。
        3. 考虑发言的完整语境，避免脱离上下文判断。`,  // 默认重要提示
        
        template: '', // 默认模板
      }
    };
  },
  mounted() {
    // 初始化 x-spreadsheet 并加载初始数据
    this.grid = new x_spreadsheet(document.getElementById('grid-container')).loadData({
      rows: {
        0: { cells: { 0: { text: '分类问题' }, 1: { text: '分类结果' } } },
      },
    });
  },
  computed: {
  classifyRequirement() {
    return [
      `角色：${this.settings.classifyRole || '未填写'}`,
      `目标：${this.settings.classifyGoal || '未填写'}`,
      `评分标准：${this.settings.scoringCriteria || '未填写'}`,
      `重要提示：${this.settings.importantNotes || '未填写'}`
    ].join('\n')
  }
},
  methods: {
    openTaskStatusDialog() {
      this.taskStatusDialogVisible = true;
      console.log('打开任务状态对话框');
     
    },
    async fetchTasks() {
      try {

        const response = await axios.get(`http://127.0.0.1:8000/task-status/${this.searchTaskId}`);
        /// response.data是一个对象，包含了任务的状态信息，但是tasks是一个数组，所以需要将response.data转换为数组
        this.tasks = [response.data];
        console.log('任务数据:', this.tasks);
      } catch (error) {
        this.$message.error('无法获取任务状态: ' + error.message);
      }
    },
    handleDownload(taskId) {
    // 方式1：直接打开新窗口（推荐）
    window.open(`http://127.0.0.1:8000/download_done_task/${taskId}`, '_blank');
    
    // 方式2：使用axios（需要处理blob数据）
    /* axios.get(`/api/download/${taskId}`, { responseType: 'blob' })
      .then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${taskId}.xlsx`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }); */
  },
    gridDataToWorksheet() {
      const gridData = this.grid.getData();
      const sheetData = Array.isArray(gridData) ? gridData[0] : gridData;

      if (!sheetData || typeof sheetData !== 'object') {
        console.error('无效的表格数据:', sheetData);
        throw new Error('表格数据无效或未定义。');
      }

      if (!sheetData.rows) {
        console.error('表格数据中缺少 rows 信息:', sheetData);
        throw new Error('表格数据中缺少 rows 信息。');
      }

      const rows = sheetData.rows;
      const worksheet = {};
      const range = { s: { r: 0, c: 0 }, e: { r: 0, c: 0 } };

      Object.keys(rows).forEach((rowIndex) => {
        if (rowIndex === 'len') return;
        const row = rows[rowIndex];
        const cells = row?.cells || {};

        Object.keys(cells).forEach((colIndex) => {
          const cell = cells[colIndex];
          if (!cell || !cell.text) return;
          const cellRef = XLSX.utils.encode_cell({ r: +rowIndex, c: +colIndex });
          worksheet[cellRef] = { v: cell.text };
          range.e.r = Math.max(range.e.r, +rowIndex);
          range.e.c = Math.max(range.e.c, +colIndex);
        });
      });

      worksheet['!ref'] = XLSX.utils.encode_range(range);
      return worksheet;
    },
    downloadFile() {
      try {
        const worksheet = this.gridDataToWorksheet();
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
        XLSX.writeFile(workbook, '已编辑文件.xlsx');
        ElNotification({
          title: '成功',
          message: '文件已成功导出！',
          type: 'success',
        });
      } catch (error) {
        console.error('导出错误:', error);
        ElNotification({
          title: '错误',
          message: '生成工作簿失败: ' + error.message,
          type: 'error',
        });
      }
    },

    handleFileChange(file) {
      this.form.file = file;
    },
    beforeUpload(file) {
      const isXLSX = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      if (!isXLSX) {
        this.$message.error('请上传有效的 xlsx 文件');
      }
      this.form.file = file;
      return isXLSX;
    },
    handleUploadSuccess(response, file) {
      this.$message.success('文件上传成功');
    },
    handleUploadError(error, file) {
      this.$message.error('文件上传失败');
    },
    async createTask() {
      if (!this.form.file) {
        this.$message.warning('请先上传文件');
        return;
      }
      const task_id = Math.random().toString(36).substr(2, 9); // 随机生成task_id
      let formData = new FormData();
      formData.append('task_id', task_id);
      formData.append('task_type', this.form.taskType);
      formData.append('file', this.form.file.raw);
      formData.append('template', this.settings.classifyRequirement);
      formData.append('classify_num', this.settings.classifyNum);
      formData.append('classify_content', this.settings.classifyContent);
      console.log('formData:', formData);
      try {
        const response = await axios.post('http://127.0.0.1:8000/start-task', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        this.$message.success('任务创建成功: ' + response.data.message);
        this.settingsDialogVisible = false; // 关闭弹窗
      } catch (error) {
        this.$message.error('任务创建失败: ' + error.message);
      }
    },
    cancelTask() {
      this.settingsDialogVisible = false; // 关闭弹窗
    },


    startClassification() {
      // 显示提示信息
      ElNotification({
        title: '提示',
        message: '任务已开始！',
        type: 'info',
      });

      // 显示进度条
      this.showProgress = true;
      this.progressPercentage = 0;
      // 调用原有的上传方法
      if (this.module == '分类模式') {
        this.uploadToServer();
      } else {
        this.ocrToServer();
      }
    },

    changeToOCR() {
          // Ensure grid is loaded and valid
    const s = this.grid;  // Assuming this.grid is the Spreadsheet instance
    // 更新第一行，从第二列开始填充 classify_content 中的元素
    const classifyContentArray_list = this.settings.classifyContent.split(',');
    classifyContentArray_list.forEach((content, index) => {
      s.cellText(0, index + 1, null);  // 第0行是表头，index+1是列索引
    });
    const classifyContentArray = ["图片URL","OCR结果"];
    console.log('分类标签:', this.settings.classifyContent);
    classifyContentArray.forEach((content, index) => {
      s.cellText(0, index, content);  // 第0行是表头，index+1是列索引
    });

    s.reRender();  // 刷新表格，确保标题更新
    this.module = 'OCR模式';
    },
    changeToClassify() {
          // Ensure grid is loaded and valid
    const s = this.grid;  // Assuming this.grid is the Spreadsheet instance
    // 更新第一行，从第二列开始填充 classify_content 中的元素
    const classifyContentArray = this.settings.classifyContent.split(',');
    console.log('分类标签:', this.settings.classifyContent);
    s.cellText(0, 0, "分类问题");
    classifyContentArray.forEach((content, index) => {
      s.cellText(0, index + 1, content);  // 第0行是表头，index+1是列索引
    });
    s.reRender();  // 刷新表格，确保标题更新
    this.module = '分类模式';
    },


    
  async uploadToServer(event) { 
  console.log('点击上传按钮');
  console.log("分类任务开始");

  try {
    // 生成随机的 task_id（任务ID）
    const taskId = Math.floor(Math.random() * 1000000);  // 随机生成任务 ID

    // Ensure grid is loaded and valid
    const s = this.grid;  // Assuming this.grid is the Spreadsheet instance
    // 更新第一行，从第二列开始填充 classify_content 中的元素
    const classifyContentArray = this.settings.classifyContent.split(',');
    console.log('分类标签:', this.settings.classifyContent);
    classifyContentArray.forEach((content, index) => {
      s.cellText(0, index + 1, content);  // 第0行是表头，index+1是列索引
    });
    s.reRender();  // 刷新表格，确保标题更新

    const rows = s.getData();  // Use the grid's API to get all the data
    const rowCount = Object.keys(rows[0].rows).length - 1;
    console.log('行数:', rowCount); 

    const questionList = [];
    for (let i = 1; i < rowCount; i++) {
      const questionContent = this.grid.cell(i, 0).text || '';
      if (questionContent) {
        questionList.push({
          question_id: i,
          question_content: questionContent,
        });
      }
    }
    if (questionList.length === 0) {
      throw new Error('未找到任何有效的分类数据。');
    }

    let offset = 0;
    const limit = this.settings.limit || 20;  // 每批上传的最大数据量
    const totalNum = questionList.length;
    const classifyContent = this.settings.classifyContent.split(',');

    // 分批次上传
    while (offset < totalNum) {
      const batchData = questionList.slice(offset, offset + limit);
      const reqData = {
        task_id: taskId,  // 使用前端生成的随机任务 ID
        total_num: totalNum,
        offset: offset,
        limit: this.settings.limit,
        classifyRequirement:this.classifyRequirement,
        classify_num: this.settings.classifyNum,
        classify_content: classifyContent,
        question_list: batchData,
      };

      console.log('准备的请求数据:', reqData);

      // Send the request to the server
      const response = await axios.post('http://localhost:8000/get_classify_result/', reqData, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      const resultData = response.data.response.data;
      if (resultData) {
        ElNotification({
          title: '成功',
          message: `分类任务第 ${offset / limit + 1} 批次已成功完成！`,
          type: 'success',
        });
        const processedRows = Math.min(offset + this.settings.limit, totalNum);
        this.progressPercentage = Math.round((processedRows / totalNum) * 100);
        // 更新表格数据
        resultData.forEach((item, index) => {
          const rowIndex = offset + index + 1;  // 表格行从第2行开始（第1行是标题）
          const result = item.result;
         

          Object.keys(result).forEach((key, colIndex) => {
            const colIndexMapped = classifyContent.indexOf(key) + 1;  // 映射到列号（从第二列开始）
            const cellValue = result[key];
            console.log("colIndexMapped:",colIndexMapped)
            console.log("cellValue:",cellValue)
            // 更新对应单元格的值
            s.cellText(rowIndex, colIndexMapped, cellValue).reRender();
          });
        });

        console.log('分类结果:', resultData);
      } else {
        throw new Error('服务器返回数据格式无效');
      }

      // 更新 offset，准备上传下一批数据
      offset += limit;
    }
  } catch (error) {
    console.error('上传错误:', error);
    ElNotification({
      title: '错误',
      message: '上传数据失败: ' + error.message,
      type: 'error',
    });
  }
},




async ocrToServer(event) { 
  console.log('点击上传按钮');
  console.log("OCR任务开始");
  try {
    // 生成随机的 task_id（任务ID）
    const taskId = Math.floor(Math.random() * 1000000);  // 随机生成任务 ID

    // Ensure grid is loaded and valid
    const s = this.grid;  // Assuming this.grid is the Spreadsheet instance
    // 更新第一行，从第二列开始填充 classify_content 中的元素
   

    const rows = s.getData();  // Use the grid's API to get all the data
    const rowCount = Object.keys(rows[0].rows).length - 1;
    console.log('行数:', rowCount); 

    const questionList = [];
    for (let i = 1; i < rowCount; i++) {
      const questionContent = this.grid.cell(i, 0).text || '';
      if (questionContent) {
        questionList.push({
          question_id: i,
          question_content: questionContent,
        });
      }
    }
    if (questionList.length === 0) {
      throw new Error('未找到任何有效的分类数据。');
    }

    let offset = 0;
    const limit = this.settings.limit || 20;  // 每批上传的最大数据量
    const totalNum = questionList.length;
    const classifyContent = this.settings.classifyContent.split(',');

    // 分批次上传
    while (offset < totalNum) {
      const batchData = questionList.slice(offset, offset + limit);
      const reqData = {
        task_id: taskId,  // 使用前端生成的随机任务 ID
        total_num: totalNum,
        offset: offset,
        limit: this.settings.limit,
        question_list: batchData,
      };

      console.log('准备的请求数据:', reqData);

      // Send the request to the server
      const response = await axios.post('http://localhost:8000/get_ocr_result/', reqData, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      const resultData = response.data.response.data;
      if (resultData) {
        ElNotification({
          title: '成功',
          message: `分类任务第 ${offset / limit + 1} 批次已成功完成！`,
          type: 'success',
        });
        const processedRows = Math.min(offset + this.settings.limit, totalNum);
        this.progressPercentage = Math.round((processedRows / totalNum) * 100);
        // 更新表格数据
        resultData.forEach((item, index) => {
          const rowIndex = offset + index + 1;  // 表格行从第2行开始（第1行是标题）
          const result = item.result;
         

          Object.keys(result).forEach((key, colIndex) => {
            const colIndexMapped = ["OCR结果"].indexOf(key) + 1;  // 映射到列号（从第二列开始）
            const cellValue = result[key];

            // 更新对应单元格的值
            s.cellText(rowIndex, colIndexMapped, cellValue).reRender();
          });
        });

        console.log('分类结果:', resultData);
      } else {
        throw new Error('服务器返回数据格式无效');
      }

      // 更新 offset，准备上传下一批数据
      offset += limit;
    }
  } catch (error) {
    console.error('上传错误:', error);
    ElNotification({
      title: '错误',
      message: '上传数据失败: ' + error.message,
      type: 'error',
    });
  }
},



    openSettingsDialog() {
      this.settingsDialogVisible = true;
      console.log('打开设置项对话框');
    },
    submitSettings() {
      // Just close the dialog and save the settings
      this.settingsDialogVisible = false;
      console.log('已更新设置:', this.settings);
    }
  }
};
</script>
