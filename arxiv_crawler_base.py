import os
import shutil
import json
import datetime
import argparse
from tqdm import tqdm
from pathlib import Path
import arxiv
import logging
import warnings
from abc import ABC, abstractmethod

# 修改日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)

# 禁用 arxiv 库的警告
warnings.filterwarnings("ignore", category=DeprecationWarning)

class ArxivCrawlerBase(ABC):
    def __init__(self, save_dir="D:/paper", days_back=14):
        """初始化爬虫基类"""
        self.save_dir = Path(save_dir)
        self.pdf_dir = self.save_dir / "pdfs"
        self.info_dir = self.save_dir / "info"
        self.markdown_dir = self.save_dir / "markdown"
        self.days_back = days_back
        
        # 创建基本目录
        for dir_path in [self.pdf_dir, self.info_dir, self.markdown_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 主要关键词（必须包含其中之一）
        self.primary_keywords = [
            "diffusion model",
            "score based",
            "generative model",
        ]
        
        # 次要关键词（可选）
        self.secondary_keywords = [
            "image generation",
            "text to image",
            "video generation",
            "3d generation",
        ]

    def build_query(self):
        """构建搜索查询"""
        primary_query = " OR ".join(f'"{kw}"' for kw in self.primary_keywords)
        secondary_query = " OR ".join(f'"{kw}"' for kw in self.secondary_keywords)
        
        query = f"({primary_query})"
        if secondary_query:
            query += f" AND ({secondary_query})"
            
        today = datetime.datetime.now()
        start_date = today - datetime.timedelta(days=self.days_back)
        
        query += f' AND lastUpdatedDate:[{start_date.strftime("%Y%m%d")}0000 TO {today.strftime("%Y%m%d")}2359]'
        query += ' AND (cat:cs.CV OR cat:cs.LG OR cat:cs.AI)'
        
        return query

    def search_papers(self, max_results=100):
        """搜索论文"""
        query = self.build_query()
        logging.info(f"搜索条件: {query}")
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        papers = list(search.results())
        filtered_papers = []
        for paper in papers:
            title_lower = paper.title.lower()
            abstract_lower = paper.summary.lower()
            
            if any(kw.lower() in title_lower or kw.lower() in abstract_lower 
                  for kw in self.primary_keywords):
                filtered_papers.append(paper)
                logging.debug(f"找到相关论文: {paper.title}")
        
        return filtered_papers

    def save_paper_info(self, paper):
        """保存论文信息"""
        paper_id = paper.get_short_id()
        pub_date = paper.updated.strftime("%Y-%m-%d")
        date_info_dir = self.get_date_dir(pub_date, self.info_dir)
        date_info_dir.mkdir(parents=True, exist_ok=True)
        
        info = {
            'id': paper_id,
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'abstract': paper.summary,
            'categories': paper.categories,
            'pdf_url': paper.pdf_url,
            'published': paper.published.strftime("%Y-%m-%d"),
            'updated': paper.updated.strftime("%Y-%m-%d"),
            'comment': paper.comment if hasattr(paper, 'comment') else None,
            'doi': paper.doi if hasattr(paper, 'doi') else None,
        }
        
        info_path = date_info_dir / f"{paper_id}.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        logging.debug(f"保存论文信息: {paper.title}")
        return True

    def generate_markdown(self, papers_by_date, date):
        """生成markdown文档"""
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = self.markdown_dir / f"papers_{date}.md"

        # 使用传入的 papers_by_date 参数
        if papers_by_date is None:
            papers_by_date = {}

        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(f"# 扩散模型相关论文 ({date})\n\n")
            
            # 按日期倒序排列
            for pub_date, date_papers in sorted(papers_by_date.items(), reverse=True):
                f.write(f"## {pub_date}\n\n")
                # 按标题排序
                date_papers.sort(key=lambda x: x.title.lower())
                
                for i, paper in enumerate(date_papers, 1):
                    paper_id = paper.get_short_id()
                    
                    # 基本信息
                    f.write(f"### {i}. {paper.title}\n\n")
                    f.write(f"**Authors:** {', '.join([author.name for author in paper.authors])}\n\n")
                    f.write(f"**arXiv:** [{paper_id}]({paper.pdf_url})\n\n")
                    
                    # 日期信息
                    f.write(f"**Submitted:** {paper.published.strftime('%Y-%m-%d')}\n")
                    f.write(f"**Updated:** {paper.updated.strftime('%Y-%m-%d')}\n\n")
                    
                    # 额外信息
                    if hasattr(paper, 'comment') and paper.comment:
                        f.write(f"**Comments:** {paper.comment}\n\n")
                    if hasattr(paper, 'doi') and paper.doi:
                        f.write(f"**DOI:** [{paper.doi}](https://doi.org/{paper.doi})\n\n")
                    
                    # 分类信息
                    f.write(f"**Categories:** {', '.join(paper.categories)}\n\n")
                    
                    # 摘要
                    f.write("**Abstract:**\n")
                    f.write(f"{paper.summary}\n\n")
                    f.write("---\n\n")
            
            # 添加统计信息
            total_papers = sum(len(papers) for papers in papers_by_date.values())
            f.write(f"\n## 统计信息\n\n")
            f.write(f"- 总论文数: {total_papers}\n")
            f.write(f"- 日期范围: {min(papers_by_date.keys())} 至 {max(papers_by_date.keys())}\n")
            f.write(f"- 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        logging.info(f"Markdown 文档已生成: {markdown_path}")

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
            
        logging.info("开始下载新论文...")
        downloaded_papers = []
        for paper in tqdm(new_papers, desc="下载进度"):
            if self.download_paper(paper):
                self.save_paper_info(paper)
                downloaded_papers.append(paper)
        
        if downloaded_papers:
            today = datetime.datetime.today().strftime("%Y-%m-%d")
            logging.info("生成markdown文档...")
            self.generate_markdown({today: downloaded_papers}, today)
            logging.info(f"markdown文档已生成: {self.markdown_dir / f'papers_{today}.md'}")

    def format_date(self, date):
        """格式化日期"""
        return date.strftime("%Y-%m-%d")

    def get_date_dir(self, date_str, base_dir):
        """获取日期文件夹路径"""
        return base_dir / date_str

    def check_paper_exists(self, paper):
        """检查论文是否已存在"""
        paper_id = paper.get_short_id()
        pub_date = self.format_date(paper.published)
        pdf_path = self.get_date_dir(pub_date, self.pdf_dir) / f"{paper_id}.pdf"
        return pdf_path.exists() 

    @abstractmethod
    def download_paper(self, paper, retry=3):
        """下载论文的抽象方法，需要在子类中实现"""
        pass