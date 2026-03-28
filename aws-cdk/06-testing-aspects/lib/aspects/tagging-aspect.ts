// ソース記事: AWS CDK #6 — CDKのテスト・Aspects・ベストプラクティスをまとめてみる
// Aspect: 全リソースにタグを付与

import * as cdk from 'aws-cdk-lib';
import { IConstruct } from 'constructs';

export class TaggingAspect implements cdk.IAspect {
  constructor(private readonly tags: Record<string, string>) {}

  visit(node: IConstruct): void {
    if (cdk.TagManager.isTaggable(node)) {
      for (const [key, value] of Object.entries(this.tags)) {
        cdk.Tags.of(node).add(key, value);
      }
    }
  }
}

// 使用例:
// const stack = new MyStack(app, 'MyStack');
// cdk.Aspects.of(stack).add(new TaggingAspect({
//   Project: 'my-project',
//   Environment: 'production',
//   Team: 'backend',
// }));
