import type {
  ExternalReferencesState,
  FieldChangeHandler,
  FormSubmitHandler,
  PostFormState,
  RelatedPostsState,
} from "../types";
import {
  ExternalReferencesPanel,
  shouldShowExternalReferencesPanel,
} from "./ExternalReferencesPanel";
import { RelatedPostsPanel, shouldShowRelatedPostsPanel } from "./RelatedPostsPanel";

interface ComposeModalProps {
  isOpen: boolean;
  postForm: PostFormState;
  relatedPosts: RelatedPostsState;
  externalReferences: ExternalReferencesState;
  onChange: FieldChangeHandler;
  onSubmit: FormSubmitHandler;
  onFindExternalReferences: () => void | Promise<void>;
  onClose: () => void;
}

export function ComposeModal({
  isOpen,
  postForm,
  relatedPosts,
  externalReferences,
  onChange,
  onSubmit,
  onFindExternalReferences,
  onClose,
}: ComposeModalProps) {
  if (!isOpen) {
    return null;
  }

  const hasSidePanel =
    shouldShowRelatedPostsPanel(relatedPosts) || shouldShowExternalReferencesPanel(externalReferences);

  return (
    <div className="modal-backdrop">
      <section className="modal-panel" role="dialog" aria-modal="true" aria-label="상담 등록">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow">Private Matching Request</p>
            <h2>상담 등록</h2>
          </div>
          <button className="ghost-button" type="button" onClick={onClose}>
            닫기
          </button>
        </div>

        <div className={hasSidePanel ? "compose-layout has-related" : "compose-layout"}>
          <form className="stack-form" onSubmit={onSubmit}>
            <label className="field">
              <span>요청 제목</span>
              <input name="title" value={postForm.title} onChange={onChange} maxLength={120} required />
            </label>
            <label className="field">
              <span>상담 내용</span>
              <textarea
                name="content"
                value={postForm.content}
                onChange={onChange}
                maxLength={10000}
                required
              />
            </label>
            <label className="field">
              <span>지역</span>
              <input
                name="region"
                value={postForm.region}
                onChange={onChange}
                maxLength={80}
                placeholder="서울, 마포구"
              />
            </label>
            <label className="field">
              <span>관심 태그</span>
              <input
                name="tags"
                value={postForm.tags}
                onChange={onChange}
                placeholder="청년, 주거, 취업, 서울"
              />
            </label>
            <div className="compose-ai-actions">
              <button
                className="ghost-button compact-button"
                type="button"
                disabled={externalReferences.isLoading}
                onClick={() => void onFindExternalReferences()}
              >
                외부 참고자료 찾기
              </button>
            </div>
            <button className="submit-button" type="submit">
              상담 등록
            </button>
          </form>
          <div className="compose-side-panels">
            <RelatedPostsPanel state={relatedPosts} />
            <ExternalReferencesPanel state={externalReferences} />
          </div>
        </div>
      </section>
    </div>
  );
}
