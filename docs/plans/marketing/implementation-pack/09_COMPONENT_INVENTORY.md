# 09 — Proposed Marketing Component Inventory

## Layout

- `MarketingLayout`
- `MarketingNavbar`
- `MobileMarketingMenu`
- `MarketingFooter`
- `SkipLink`
- `MarketingContainer`
- `MarketingSection`
- `SectionHeader`
- `SectionRule`

## Brand

- `DimaWordmark`
- `DimaMark`
- `DimaPillarMark`
- `EvidenceLabel`
- `CapabilityStatusBadge`

## Hero/proof

- `MarketingHero`
- `ProductProofFrame`
- `QueryComposerDemo`
- `ContextTagList`
- `ValidationTimeline`
- `ResultPreview`
- `SqlPreview`
- `TracePreview`
- `ProofAnnotation`

## Content

- `PillarGrid`
- `PillarCard`
- `WorkflowSteps`
- `UseCaseGrid`
- `UseCaseCard`
- `IndustryProof`
- `SecurityFeatureList`
- `IntegrationFlow`
- `ArchitectureDiagram`
- `FaqList`
- `FinalCta`

## Pages

- `ProductCapabilitySection`
- `HowItWorksStep`
- `SolutionOutcomeCard`
- `TextileQuestionCard`
- `SecurityBoundaryCard`
- `IntegrationStatusTable`
- `ContactForm`

## Reuse rules

- Page files compose sections; they do not contain large local UI implementations.
- Copy resides in typed content/i18n.
- Data arrays are not duplicated.
- A component is shared only when semantics match, not only visual similarity.
- Avoid a universal “Card” with dozens of variants.
- Server component by default.
- Client components isolated to menu/form/proof interaction.
- No component should require product QueryClient or stores.

## Proposed source structure

```text
src/components/marketing/
  brand/
    DimaWordmark.tsx
    EvidenceLabel.tsx
    CapabilityStatusBadge.tsx
  layout/
    MarketingNavbar.tsx
    MobileMarketingMenu.tsx
    MarketingFooter.tsx
    MarketingContainer.tsx
    MarketingSection.tsx
  proof/
    ProductProofFrame.tsx
    QueryComposerDemo.tsx
    ValidationTimeline.tsx
    ResultPreview.tsx
  sections/
    MarketingHero.tsx
    PillarGrid.tsx
    WorkflowSteps.tsx
    UseCaseGrid.tsx
    IndustryProof.tsx
    TrustArchitecture.tsx
    FaqList.tsx
    FinalCta.tsx
  forms/
    ContactForm.tsx
```

## Import boundary

Allowed:
- `components/ui`
- `lib/utils`
- `lib/motion`
- `content/marketing`
- i18n
- `lucide-react`
- `motion/react` only in client islands

Avoid:
- product `stores`
- `api-client`
- `@tanstack/react-query`
- product shell
- report/chart modules
- React Flow
- backend calls on homepage

## Component acceptance checklist

Each component:
- semantic element,
- accessible name,
- keyboard behavior if interactive,
- dark/light,
- mobile,
- no hardcoded duplicate copy,
- no layout shift,
- reduced motion,
- typed props,
- no `any`,
- no arbitrary z-index without scale,
- no magic brand colors outside tokens.
