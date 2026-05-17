import requests
import random
import pandas as pd
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Photo(BaseModel):
    albumId: int
    id: int
    title: str
    url: str
    thumbnailUrl: Optional[str] = None

    # 後で追加するフィールド
    stock: int = Field(default=0, ge=0)
    price: int = Field(default=0, gt=0)
    stock_status: str = Field(default="不明")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if v:
            return v.strip().capitalize()
        return v


def main():
    try:
        url = "https://jsonplaceholder.typicode.com/photos"

        print("🌐 APIからデータを取得中...")

        response = requests.get(url, timeout=15)
        response.raise_for_status()  # 4xx, 5xxエラーを例外化

        raw_data = response.json()
        print(f"✅ {len(raw_data)}件のデータを取得しました")

        photos = []
        for item in raw_data[:10]:  # 50件に制限（テスト用）
            photo = Photo.model_validate(item)

            # 後で追加するデータ
            photo.stock = random.randint(10, 200)
            photo.price = int(photo.stock * 120 * 1.1)

            # 在庫ステータス判定
            if photo.stock >= 100:
                photo.stock_status = "良好"
            elif photo.stock >= 30:
                photo.stock_status = "要注意"
            else:
                photo.stock_status = "危険"

            photos.append(photo)

        # ==================== Pandas処理 ====================
        # Pydantic → DataFrame（最適な変換方法）
        box = []
        for p in photos:
            back = p.model_dump()
            box.append(back)

        df = pd.DataFrame(box)

        # ==================== 出力 ====================
        # 全商品データ
        df.to_csv("all_products.csv", index=False, encoding="utf-8")
        print("✅ all_products.csv を保存しました")

        # ==================== 集計 ====================
        print("\n=== 集計結果 ===")
        print(f"総商品数: {len(df)}件")
        print(f"平均価格: {df['price'].mean():,.0f}円")
        print(f"平均在庫数: {df['stock'].mean():,.1f}個")

    except requests.exceptions.RequestException as e:
        print(f"❌ APIリクエストエラー: {e}")
    except Exception as e:
        print(f"❌ 予期せぬエラー: {e}")


if __name__ == "__main__":
    main()
