import { database } from '@/lib/firebase';
import { ref, query, orderByChild, limitToLast, get, onValue, Unsubscribe } from 'firebase/database';

export interface NewsArticle {
  id: string;
  title: string;
  description: string;
  content: string;
  imageUrl: string;
  source: string;
  category: string;
  author: string;
  publishedAt: number;
  updatedAt: number;
  views: number;
  likes: number;
  isFeatured: boolean;
  url?: string;
}

export interface NewsCategory {
  id: string;
  name: string;
  icon: string;
}

class NewsService {
  private newsRef = ref(database, 'news');
  private categoriesRef = ref(database, 'categories');

  /**
   * Fetch all news articles with optional filtering
   */
  async getArticles(limit: number = 50, category?: string): Promise<NewsArticle[]> {
    try {
      let articlesRef = this.newsRef;
      
      if (category && category !== 'all') {
        articlesRef = ref(database, `news/categories/${category}`);
      }

      const snapshot = await get(articlesRef);
      
      if (!snapshot.exists()) {
        return [];
      }

      const articles: NewsArticle[] = [];
      snapshot.forEach((childSnapshot) => {
        const article = {
          id: childSnapshot.key || '',
          ...childSnapshot.val(),
        };
        articles.push(article);
      });

      // Sort by publishedAt in descending order
      return articles
        .sort((a, b) => (b.publishedAt || 0) - (a.publishedAt || 0))
        .slice(0, limit);
    } catch (error) {
      console.error('Error fetching articles:', error);
      return [];
    }
  }

  /**
   * Fetch a single article by ID
   */
  async getArticleById(articleId: string): Promise<NewsArticle | null> {
    try {
      const articleRef = ref(database, `news/${articleId}`);
      const snapshot = await get(articleRef);

      if (!snapshot.exists()) {
        return null;
      }

      return {
        id: snapshot.key || '',
        ...snapshot.val(),
      };
    } catch (error) {
      console.error('Error fetching article:', error);
      return null;
    }
  }

  /**
   * Search articles by title or description
   */
  async searchArticles(searchTerm: string): Promise<NewsArticle[]> {
    try {
      const articles = await this.getArticles(100);
      const lowerSearchTerm = searchTerm.toLowerCase();

      return articles.filter(
        (article) =>
          article.title.toLowerCase().includes(lowerSearchTerm) ||
          article.description.toLowerCase().includes(lowerSearchTerm)
      );
    } catch (error) {
      console.error('Error searching articles:', error);
      return [];
    }
  }

  /**
   * Get featured articles
   */
  async getFeaturedArticles(limit: number = 10): Promise<NewsArticle[]> {
    try {
      const articles = await this.getArticles(100);
      return articles.filter((article) => article.isFeatured).slice(0, limit);
    } catch (error) {
      console.error('Error fetching featured articles:', error);
      return [];
    }
  }

  /**
   * Get articles by category
   */
  async getArticlesByCategory(category: string, limit: number = 50): Promise<NewsArticle[]> {
    return this.getArticles(limit, category);
  }

  /**
   * Subscribe to real-time article updates
   */
  subscribeToArticles(callback: (articles: NewsArticle[]) => void): Unsubscribe {
    return onValue(this.newsRef, (snapshot) => {
      const articles: NewsArticle[] = [];

      if (snapshot.exists()) {
        snapshot.forEach((childSnapshot) => {
          const article = {
            id: childSnapshot.key || '',
            ...childSnapshot.val(),
          };
          articles.push(article);
        });
      }

      // Sort by publishedAt in descending order
      articles.sort((a, b) => (b.publishedAt || 0) - (a.publishedAt || 0));
      callback(articles);
    });
  }

  /**
   * Get all available categories
   */
  async getCategories(): Promise<NewsCategory[]> {
    try {
      const snapshot = await get(this.categoriesRef);

      if (!snapshot.exists()) {
        return [];
      }

      const categories: NewsCategory[] = [];
      snapshot.forEach((childSnapshot) => {
        const category = {
          id: childSnapshot.key || '',
          ...childSnapshot.val(),
        };
        categories.push(category);
      });

      return categories;
    } catch (error) {
      console.error('Error fetching categories:', error);
      return [];
    }
  }

  /**
   * Increment article view count
   */
  async incrementViewCount(articleId: string): Promise<void> {
    try {
      const viewsRef = ref(database, `news/${articleId}/views`);
      const snapshot = await get(viewsRef);
      const currentViews = snapshot.val() || 0;
      
      // In a real app, you'd use a transaction for this
      // For now, just increment locally
    } catch (error) {
      console.error('Error incrementing view count:', error);
    }
  }

  /**
   * Like an article
   */
  async likeArticle(articleId: string): Promise<void> {
    try {
      const likesRef = ref(database, `news/${articleId}/likes`);
      const snapshot = await get(likesRef);
      const currentLikes = snapshot.val() || 0;
      
      // In a real app, you'd use a transaction for this
    } catch (error) {
      console.error('Error liking article:', error);
    }
  }
}

export const newsService = new NewsService();
