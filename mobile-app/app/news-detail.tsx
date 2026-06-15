import { useEffect, useState } from 'react';
import { ScrollView, Text, View, TouchableOpacity, Image, Share, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ScreenContainer } from '@/components/screen-container';
import { newsService, NewsArticle } from '@/lib/services/news-service';
import { useColors } from '@/hooks/use-colors';
import * as Clipboard from 'expo-clipboard';

export default function NewsDetailScreen() {
  const router = useRouter();
  const colors = useColors();
  const { articleId } = useLocalSearchParams<{ articleId: string }>();
  const [article, setArticle] = useState<NewsArticle | null>(null);
  const [loading, setLoading] = useState(true);
  const [isFavorited, setIsFavorited] = useState(false);

  useEffect(() => {
    loadArticle();
  }, [articleId]);

  const loadArticle = async () => {
    if (!articleId) {
      router.back();
      return;
    }

    try {
      setLoading(true);
      const fetchedArticle = await newsService.getArticleById(articleId);
      if (fetchedArticle) {
        setArticle(fetchedArticle);
        await newsService.incrementViewCount(articleId);
      }
    } catch (error) {
      console.error('Error loading article:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleShare = async () => {
    if (!article) return;

    try {
      await Share.share({
        message: `${article.title}\n\n${article.description}\n\nRead more on GenZ Frontier`,
        url: article.url || 'https://www.genzfrontir.com',
        title: article.title,
      });
    } catch (error) {
      console.error('Error sharing:', error);
    }
  };

  const handleCopyLink = async () => {
    if (!article?.url) return;

    try {
      await Clipboard.setStringAsync(article.url);
      alert('Link copied to clipboard!');
    } catch (error) {
      console.error('Error copying link:', error);
    }
  };

  const handleToggleFavorite = () => {
    setIsFavorited(!isFavorited);
    // TODO: Save to favorites in AsyncStorage or Firebase
  };

  if (loading) {
    return (
      <ScreenContainer className="flex-1 justify-center items-center">
        <ActivityIndicator size="large" color={colors.primary} />
      </ScreenContainer>
    );
  }

  if (!article) {
    return (
      <ScreenContainer className="flex-1 justify-center items-center">
        <Text className="text-lg font-semibold" style={{ color: colors.foreground }}>
          Article not found
        </Text>
        <TouchableOpacity
          onPress={() => router.back()}
          className="mt-4 px-6 py-3 rounded-lg"
          style={{ backgroundColor: colors.primary }}
        >
          <Text className="text-white font-semibold">Go Back</Text>
        </TouchableOpacity>
      </ScreenContainer>
    );
  }

  return (
    <ScreenContainer className="p-0">
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Hero Image */}
        {article.imageUrl && (
          <Image
            source={{ uri: article.imageUrl }}
            className="w-full h-64"
            resizeMode="cover"
          />
        )}

        {/* Content */}
        <View className="px-4 py-6">
          {/* Header */}
          <View className="mb-4">
            <View className="flex-row items-center mb-3">
              <Text className="text-xs font-semibold px-2 py-1 rounded-full bg-primary text-white">
                {article.category}
              </Text>
              <Text className="text-xs ml-2" style={{ color: colors.muted }}>
                {new Date(article.publishedAt).toLocaleDateString()}
              </Text>
            </View>

            <Text
              className="text-2xl font-bold mb-3"
              style={{ color: colors.foreground }}
            >
              {article.title}
            </Text>

            <View className="flex-row justify-between items-center mb-4 pb-4 border-b" style={{ borderColor: colors.border }}>
              <View>
                <Text className="text-xs" style={{ color: colors.muted }}>
                  By {article.author || 'GenZ Frontier'}
                </Text>
                <Text className="text-xs mt-1" style={{ color: colors.muted }}>
                  {article.source}
                </Text>
              </View>
              <Text className="text-xs" style={{ color: colors.muted }}>
                👁️ {article.views || 0} views
              </Text>
            </View>
          </View>

          {/* Description */}
          <Text
            className="text-base mb-4 leading-relaxed"
            style={{ color: colors.foreground }}
          >
            {article.description}
          </Text>

          {/* Full Content */}
          <Text
            className="text-base mb-6 leading-relaxed"
            style={{ color: colors.foreground }}
          >
            {article.content}
          </Text>

          {/* Action Buttons */}
          <View className="flex-row gap-3 mb-6">
            <TouchableOpacity
              onPress={handleShare}
              className="flex-1 flex-row items-center justify-center py-3 rounded-lg border"
              style={{ borderColor: colors.primary }}
            >
              <Text className="text-sm font-semibold" style={{ color: colors.primary }}>
                📤 Share
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={handleCopyLink}
              className="flex-1 flex-row items-center justify-center py-3 rounded-lg border"
              style={{ borderColor: colors.primary }}
            >
              <Text className="text-sm font-semibold" style={{ color: colors.primary }}>
                🔗 Copy Link
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={handleToggleFavorite}
              className="flex-1 flex-row items-center justify-center py-3 rounded-lg"
              style={{ backgroundColor: isFavorited ? colors.primary : colors.surface }}
            >
              <Text
                className="text-sm font-semibold"
                style={{ color: isFavorited ? 'white' : colors.primary }}
              >
                {isFavorited ? '❤️ Saved' : '🤍 Save'}
              </Text>
            </TouchableOpacity>
          </View>

          {/* Back Button */}
          <TouchableOpacity
            onPress={() => router.back()}
            className="py-3 rounded-lg"
            style={{ backgroundColor: colors.surface }}
          >
            <Text className="text-center font-semibold" style={{ color: colors.foreground }}>
              ← Back to News
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </ScreenContainer>
  );
}
