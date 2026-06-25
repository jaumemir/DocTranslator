<template>
  <div class="vip-card">
    <div class="vip-card__corner vip-card__corner--tl"></div>
    <div class="vip-card__corner vip-card__corner--tr"></div>
    <div class="vip-card__corner vip-card__corner--bl"></div>
    <div class="vip-card__corner vip-card__corner--br"></div>

    <div class="vip-card__content">
      <div class="vip-card__badge">
        <el-icon class="crown-icon"><StarFilled /></el-icon>
        <span>VIP</span>
      </div>
      <h3 class="vip-card__title">尊享会员特权</h3>
      <p class="vip-card__desc">您已成为DocTranslator会员</p>

      <div class="vip-card__benefits">
        <div class="benefit-item">
          <el-icon size="20"><Check /></el-icon>
          <span>专属高速翻译通道</span>
        </div>
        <div class="benefit-item">
          <el-icon size="20"><Check /></el-icon>
          <span>优先技术支持</span>
        </div>
        <div class="benefit-item">
          <el-icon size="20"><Check /></el-icon>
          <span>更高翻译质量</span>
        </div>
        <span class="label-with-ad">
          <el-tag
            size="mini"
            type="warning"
            style="margin-left: 8px; cursor: pointer; font-size: medium"
            @click="visitSite"
          >
            🔥 推荐使用在线api中转站
          </el-tag>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
const visitSite = () => {
  window.open('https://api.ezworkapi.top', '_blank')
}
</script>
<style scoped>
/* VIP card responsive design */
.vip-card {
  position: relative;
  margin-bottom: 20px;
  padding: 2px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
  box-shadow: 0 4px 12px rgba(253, 160, 133, 0.2);
  overflow: hidden;
}
.vip-card__content {
  position: relative;
  padding: 20px 15px;
  background: white;
  border-radius: 10px;
  z-index: 2;
}
/* Mobile-first corner design */
.vip-card__corner {
  position: absolute;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
  z-index: 1;
}
.vip-card__corner--tl {
  top: 0;
  left: 0;
  clip-path: polygon(0 0, 0% 100%, 100% 0);
}
.vip-card__corner--tr {
  top: 0;
  right: 0;
  clip-path: polygon(0 0, 100% 0, 100% 100%);
}
.vip-card__corner--bl {
  bottom: 0;
  left: 0;
  clip-path: polygon(0 0, 0% 100%, 100% 100%);
}
.vip-card__corner--br {
  bottom: 0;
  right: 0;
  clip-path: polygon(100% 0, 0% 100%, 100% 100%);
}
/* Responsive badge */
.vip-card__badge {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
  border-radius: 18px;
  color: white;
  font-weight: bold;
  margin-bottom: 12px;
  font-size: 14px;
}
.crown-icon {
  margin-right: 6px;
  font-size: 14px;
}
/* Responsive text size */
.vip-card__title {
  margin: 0 0 8px;
  font-size: 18px;
  color: #333;
  line-height: 1.3;
}
.vip-card__desc {
  margin: 0 0 15px;
  color: #666;
  font-size: 13px;
  line-height: 1.4;
}
/* Responsive benefits list */
.vip-card__benefits {
  display: grid;
  gap: 10px;
}
.benefit-item {
  display: flex;
  align-items: center;
  color: #333;
  font-size: 13px;
}
.benefit-item .el-icon {
  margin-right: 6px;
  color: #f6d365;
  font-size: 16px;
  font-weight: bolder;
}
/* Tablet and desktop adaptation */
@media (min-width: 768px) {
  .vip-card {
    margin-bottom: 30px;
  }

  .vip-card__content {
    padding: 25px;
  }

  .vip-card__corner {
    width: 60px;
    height: 60px;
  }

  .vip-card__badge {
    padding: 6px 12px;
    font-size: 15px;
  }

  .crown-icon {
    font-size: 16px;
  }

  .vip-card__title {
    font-size: 20px;
  }

  .vip-card__desc {
    font-size: 14px;
  }

  .benefit-item {
    font-size: 14px;
  }
}
</style>
