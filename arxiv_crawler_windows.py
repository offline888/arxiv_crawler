import logging
import time
import subprocess
from pathlib import Path
from arxiv_crawler_base import ArxivCrawlerBase
import argparse
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime

class ArxivCrawlerWindows(ArxivCrawlerBase):
    def __init__(self, save_dir="D:/paper", days_back=14, max_workers=5):
        """初始化爬虫
        Args:
            save_dir: 保存目录
            days_back: 向前查找的天数
            max_workers: 最大并行下载数
        """
        super().__init__(save_dir, days_back)
        self.max_workers = max_workers

    def download_paper(self, paper, retry=3):
        """实现基类的抽象方法"""
        success, _ = self.download_single_paper(paper, retry)
        return None  # 修改返回值为None以匹配基类方法

    def download_single_paper(self, paper, retry=3):
        """下载单篇论文"""
        paper_id = paper.get_short_id()
        pub_date = paper.published.strftime("%Y-%m-%d")
        date_pdf_dir = self.pdf_dir / pub_date
        date_pdf_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_path = date_pdf_dir / f"{paper_id}.pdf"
        
        if pdf_path.exists():
            logging.debug(f"论文已存在: {paper.title}")
            return True, paper
            
        logging.info(f"正在下载: {paper.title}")
        
        # 尝试使用 IDM 命令行下载
        try:
            idm_paths = [
                r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe",
                r"C:\Program Files\Internet Download Manager\IDMan.exe"
            ]
            idm_exe = None
            for path in idm_paths:
                if os.path.exists(path):
                    idm_exe = path
                    break
                    
            if idm_exe:
                cmd = [
                    idm_exe,
                    "/d", paper.pdf_url,  # 下载链接
                    "/p", str(date_pdf_dir),  # 保存路径
                    "/f", f"{paper_id}.pdf",  # 文件名
                    "/q",  # 下载完成后退出
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # 等待下载完成
                timeout = 300  # 5分钟超时
                start_time = time.time()
                while not pdf_path.exists():
                    if time.time() - start_time > timeout:
                        logging.error(f"IDM 下载超时: {paper.title}")
                        break
                    time.sleep(1)
                    
                if pdf_path.exists():
                    logging.debug(f"IDM 下载成功: {paper.title}")
                    return True, paper
                    
            else:
                logging.warning("未找到 IDM 安装路径,尝试普通下载")
                
        except Exception as e:
            logging.warning(f"IDM 下载失败: {str(e)}, 尝试普通下载")
            
        # 如果 IDM 下载失败,使用普通下载方式
        for attempt in range(retry):
            try:
                response = requests.get(paper.pdf_url, timeout=30)
                if response.status_code == 200:
                    with open(pdf_path, "wb") as f:
                        f.write(response.content)
                    logging.debug(f"普通下载成功: {paper.title}")
                    return True, paper
                else:
                    logging.warning(f"下载失败 (尝试 {attempt+1}/{retry}): 状态码 {response.status_code}")
            except Exception as e:
                logging.warning(f"下载失败 (尝试 {attempt+1}/{retry}): {str(e)}")
                time.sleep(3)  # 失败后等待一会再重试
                
        logging.error(f"所有下载方式均失败: {paper.title}")
        return False, paper

    def run(self):
        """运行爬虫"""
        logging.info("开始搜索论文...")
        papers = self.search_papers()
        logging.info(f"找到 {len(papers)} 篇相关论文")
        
        new_papers = [paper for paper in papers if not self.check_paper_exists(paper)]
        logging.info(f"其中 {len(new_papers)} 篇是新论文")

        if not new_papers:
            logging.info("没有新的论文需要下载")
            return
            
        logging.info("开始并行下载新论文...")
        downloaded_papers = []
        
        # 使用线程池进行并行下载
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有下载任务
            future_to_paper = {
                executor.submit(self.download_single_paper, paper): paper 
                for paper in new_papers
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_paper):
                success, paper = future.result()
                if success:
                    self.save_paper_info(paper)
                    downloaded_papers.append(paper)
        
        if downloaded_papers:
            today = datetime.datetime.today().strftime("%Y-%m-%d")
            logging.info("生成markdown文档...")
            self.generate_markdown({today: downloaded_papers}, today)
            logging.info(f"markdown文档已生成: {self.markdown_dir / f'papers_{today}.md'}")

def main():
    parser = argparse.ArgumentParser(description='ArXiv论文爬虫 (Windows)')
    parser.add_argument('--days', type=int, default=14, help='向前查找的天数')
    parser.add_argument('--dir', type=str, default='D:/papers', help='保存目录')
    parser.add_argument('--workers', type=int, default=5, help='最大并行下载数')
    args = parser.parse_args()
    
    crawler = ArxivCrawlerWindows(
        save_dir=args.dir,
        days_back=args.days,
        max_workers=args.workers
    )
    crawler.run()

if __name__ == "__main__":
    main() 