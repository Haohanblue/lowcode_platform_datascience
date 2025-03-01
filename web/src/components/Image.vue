<template>
  <div class="upload-container">
    <!-- 上传组件 -->
    <el-upload
      ref="upload"
      class="upload-demo"
      drag
      :action="uploadUrl"
      :show-file-list="false"
      multiple
      :before-upload="beforeUpload"
      @change="handleFileChange"
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">
        Drop file here or <em>click to upload</em>
      </div>
    </el-upload>

    <!-- 文件选择后显示的进度 -->
    <div v-if="selectedFiles.length > 0" class="upload-progress-container">
      <h4 class="progress-title">正在上传文件：{{ selectedFiles.length }} 张图片</h4>
      <el-progress 
        :percentage="uploadProgress" 
        status="active" 
        striped 
        striped-flow 
        :text-inside="true" 
        :stroke-width="22" 
        class="upload-progress"
      />
      <el-button 
        @click="uploadFiles" 
        type="primary" 
        class="upload-button" 
        :disabled="!selectedFiles.length"
      >
        直接识别OCR
      </el-button>

      <el-button 
        @click="get_url" 
        type="primary" 
        class="upload-button" 
        :disabled="!selectedFiles.length"
      >
        上传图片至图床
      </el-button>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <!-- OCR 结果展示 -->
    <div v-if="ocrResult.length > 0" class="ocr-result-container">
      <h4 class="ocr-result-title">任务识别结果：</h4>
      <el-table :data="ocrResult" style="width: 100%">
        <el-table-column prop="seq_id" label="任务序号" width="100"></el-table-column>
        <el-table-column prop="image_name" label="图片名称" width="200"></el-table-column>
        <el-table-column prop="ocr_result" label="识别结果" width="500"></el-table-column>
      </el-table>
      <el-button 
        @click="downloadResult" 
        type="primary" 
        class="download-button"
      >
        下载完整结果
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { UploadFilled } from '@element-plus/icons-vue';
import axios from "axios";
import { ElMessage } from 'element-plus';  // 引入 Element Plus 的消息提示组件
import * as XLSX from 'xlsx';  // 引入 xlsx 库

const uploadUrl = "http://127.0.0.1:8000/upload/";
const downloadUrl = "http://127.0.0.1:8000/download/";

const get_img_url = "http://127.0.0.1:8000/upload_image/"

const selectedFiles = ref([]);  // 存储选择的文件
const error = ref(null);  // 存储错误信息
const taskId = ref(null);  // 存储任务ID
const uploadProgress = ref(0);  // 上传进度
const currentSeqId = ref(0);  // 当前上传的图片序号
const ocrResult = ref([]);  // OCR结果（以表格方式展示）

const beforeUpload = (file) => {
  console.log("beforeUpload", file);
  return false;  // 阻止默认上传
};

const generateTaskId = () => {
  taskId.value = Math.random().toString(36).substr(2, 9);  // 生成随机ID
};

const handleFileChange = (file, fileList) => {
  error.value = null;
  selectedFiles.value = fileList;
};

const get_url = async () => {
  if (selectedFiles.value.length === 0) {
    error.value = "请先选择文件。";
    return;
  }

  if (!taskId.value) {
    generateTaskId();  // 如果没有任务ID，则生成一个
  }

  let completedCount = 0;

  // 开始逐个上传文件
  for (let i = 0; i < selectedFiles.value.length; i++) {
    const file = selectedFiles.value[i];
    const formData = new FormData();
    formData.append("file", file.raw);
    formData.append("task_id", taskId.value);
    formData.append("seq_id", i + 1);  // 设置顺序id

    try {
      const response = await axios.post(get_img_url, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      completedCount++;
      currentSeqId.value = i + 1;  // 更新当前上传的图片序号
      uploadProgress.value = Math.round((completedCount / selectedFiles.value.length) * 100);  // 更新进度
      const ocr_result = response.data.img_url;
      // 上传成功后，将响应数据添加到 OCR 结果中
      const { seq_id, image_name } = response.data;
      ocrResult.value.push({
        seq_id,
        image_name,
        ocr_result
      });

      // 判断是否上传完所有文件
      if (completedCount === selectedFiles.value.length) {
        ElMessage.success("所有文件上传完成！");  // 提示上传完成
      }
    } catch (err) {
      error.value = `文件 ${i + 1} 上传失败: ${err.response?.data?.error || err.message}`;
      break;
    }
  }
};


const uploadFiles = async () => {
  if (selectedFiles.value.length === 0) {
    error.value = "请先选择文件。";
    return;
  }

  if (!taskId.value) {
    generateTaskId();  // 如果没有任务ID，则生成一个
  }

  let completedCount = 0;

  // 开始逐个上传文件
  for (let i = 0; i < selectedFiles.value.length; i++) {
    const file = selectedFiles.value[i];
    const formData = new FormData();
    formData.append("file", file.raw);
    formData.append("task_id", taskId.value);
    formData.append("seq_id", i + 1);  // 设置顺序id

    try {
      const response = await axios.post(uploadUrl, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      completedCount++;
      currentSeqId.value = i + 1;  // 更新当前上传的图片序号
      uploadProgress.value = Math.round((completedCount / selectedFiles.value.length) * 100);  // 更新进度

      // 上传成功后，将响应数据添加到 OCR 结果中
      const { seq_id, image_name, ocr_result } = response.data;
      ocrResult.value.push({
        seq_id,
        image_name,
        ocr_result
      });

      // 判断是否上传完所有文件
      if (completedCount === selectedFiles.value.length) {
        ElMessage.success("所有文件上传完成！");  // 提示上传完成
      }
    } catch (err) {
      error.value = `文件 ${i + 1} 上传失败: ${err.response?.data?.error || err.message}`;
      break;
    }
  }
};

const downloadResult = async () => {
  try {
    // 发送 GET 请求获取 XLSX 文件
    const response = await axios.get(`${downloadUrl}${taskId.value}`, { responseType: 'blob' });

    // 创建下载链接
    const link = document.createElement('a');
    const blob = response.data;
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.download = `ocr_result_${taskId.value}.xlsx`;  // 设置下载文件名
    link.click();

    // 释放 URL 对象
    URL.revokeObjectURL(url);
  } catch (err) {
    error.value = `下载OCR结果失败: ${err.response?.data?.error || err.message}`;
  }
};
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.upload-demo {
  border: 2px dashed #409EFF;
  padding: 40px;
  text-align: center;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 30px;
}

.upload-demo .el-upload__text {
  font-size: 16px;
  color: #409EFF;
}

.upload-progress-container {
  margin-top: 30px;
  text-align: center;
}

.progress-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
}

.upload-progress {
  margin: 20px auto;
}

.upload-button {
  width: 200px;
  margin-top: 20px;
  font-size: 16px;
}

.error-message {
  color: red;
  margin-top: 20px;
  font-size: 14px;
}

.ocr-result-container {
  margin-top: 40px;
}

.ocr-result-title {
  font-size: 20px;
  color: #333;
  margin-bottom: 20px;
}

.download-button {
  margin-top: 20px;
  width: 200px;
}
</style>
