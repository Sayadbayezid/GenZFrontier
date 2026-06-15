import { useEffect, useState } from 'react';
import { ScrollView, Text, View, TouchableOpacity, FlatList, RefreshControl, Image, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { ScreenContainer } from '@/components/screen-container';
import { newsService, NewsArticle } from '@/lib/services/news-service';
import { useColors } from '@/hooks/use-colors';

export default function HomeScreen() {
  const router = useRouter();
  const colors = useColors();
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', name: 'All News', icon: '📰' },
    { id: 'technology', name: 'Tech', icon: '💻' },
    { id: 'business', name: 'Business', icon: '💼' },
    { id: 'entertainment', name: 'Entertainment', icon: '🎬' },
    { id: 'sports', name: 'Sports', icon: '⚽' },
  ];

  useEffect(() => {
    loadArticles();
  }, [selectedCategory]);

  const loadArticles = async () => {
    try {
      setLoading(true);
      const fetchedArticles = await newsService.getArticles(50, selectedCategory);
      setArticles(fetchedArticles);
    } catch (error) {
      console.error('Error loading articles:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadArticles();
    setRefreshing(false);
  };

  const handleArticlePress = (article: NewsArticle) => {
    router.push({
      pathname: '/news-detail',
      params: { articleId: article.id },
    });
  };

  const renderArticleCard = ({ item }: { item: NewsArticle }) => (
    <TouchableOpacity
      onPress={() => handleArticlePress(item)}
      className="mb-4 rounded-xl overflow-hidden bg-surface border border-border"
      style={{ backgroundColor: colors.surface }}
    >
      {item.imageUrl && (
        <Image
          source={{ uri: item.imageUrl }}
          className="w-full h-48"
          resizeMode="cover"
        />
      )}
      <View className="p-4">
        <View className="flex-row items-center mb-2">
          <Text className="text-xs font-semibold px-2 py-1 rounded-full bg-primary text-white">
            {item.category}
          </Text>
          <Text className="text-xs ml-2" style={{ color: colors.muted }}>
            {new Date(item.publishedAt).toLocaleDateString()}
          </Text>
        </View>
        <Text
          className="text-base font-bold mb-2"
          style={{ color: colors.foreground }}
          numberOfLines={2}
        >
          {item.title}
        </Text>
        <Text
          className="text-sm mb-3"
          style={{ color: colors.muted }}
          numberOfLines={2}
        >
          {item.description}
        </Text>
        <View className="flex-row justify-between items-center">
          <Text className="text-xs" style={{ color: colors.muted }}>
            {item.source}
          </Text>
          <Text className="text-xs" style={{ color: colors.muted }}>
            👁️ {item.views || 0}
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <ScreenContainer className="p-0">
      {/* Header */}
      <View className="px-4 pt-4 pb-2" style={{ backgroundColor: colors.background }}>
        <Text className="text-3xl font-bold" style={{ color: colors.foreground }}>
          GenZ Frontier
        </Text>
        <Text className="text-sm" style={{ color: colors.muted }}>
          Stay updated with latest news
        </Text>
      </View>

      {/* Category Filter */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        className="px-4 py-3"
        style={{ backgroundColor: colors.background }}
      >
        {categories.map((category) => (
          <TouchableOpacity
            key={category.id}
            onPress={() => setSelectedCategory(category.id)}
            className={`mr-3 px-4 py-2 rounded-full border ${
              selectedCategory === category.id
                ? 'bg-primary border-primary'
                : 'bg-surface border-border'
            }`}
            style={{
              backgroundColor: selectedCategory === category.id ? colors.primary : colors.surface,
              borderColor: selectedCategory === category.id ? colors.primary : colors.border,
            }}
          >
            <Text
              className={`text-sm font-semibold ${
                selectedCategory === category.id ? 'text-white' : ''
              }`}
              style={{
                color: selectedCategory === category.id ? 'white' : colors.foreground,
              }}
            >
              {category.icon} {category.name}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* News Feed */}
      {loading && !refreshing ? (
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : (
        <FlatList
          data={articles}
          renderItem={renderArticleCard}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 20 }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
          ListEmptyComponent={
            <View className="flex-1 justify-center items-center py-20">
              <Text className="text-lg font-semibold" style={{ color: colors.foreground }}>
                No articles found
              </Text>
              <Text className="text-sm mt-2" style={{ color: colors.muted }}>
                Try a different category or check back later
              </Text>
            </View>
          }
        />
      )}
    </ScreenContainer>
  );
}
