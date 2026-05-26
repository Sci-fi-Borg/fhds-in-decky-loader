import {
  definePlugin, PanelSection, PanelSectionRow,
  ToggleField, SliderField, ButtonItem,
} from "@decky/ui";

const API_VERSION = 2;
const manifest = { name: "FHDS Trigger Effects" };
const conn = (window as any).__DECKY_SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED_deckyLoaderAPIInit;
const api: any = conn?.connect(API_VERSION, manifest.name) || {};
const call = (api?.call || (() => Promise.reject("no api"))).bind(api);

const R = (window as any).SP_REACT;

// Detect system language
const lang = (navigator.language || "en").startsWith("zh") ? "zh" : "en";

const T = {
  zh: {
    title: "FHDS 扳机",
    brake: "刹车（左扳机）",
    brakeOn: "刹车效果",
    brakeMax: "最大力度",
    brakeCurve: "力度曲线",
    abs: "ABS 弹跳",
    throttle: "油门（右扳机）",
    throttleOn: "油门效果",
    throttleMax: "最大力度",
    gearShift: "换挡冲击",
    revLimit: "转速限制器",
    enable: "扳机效果",
    advanced: "高级",
    reset: "恢复默认设置",
  },
  en: {
    title: "FHDS Triggers",
    enable: "Trigger Effects",
    brake: "Brake (L2)",
    brakeOn: "Brake Effects",
    brakeMax: "Max Force",
    brakeCurve: "Curve",
    abs: "ABS Buzz",
    throttle: "Throttle (R2)",
    throttleOn: "Throttle Effects",
    throttleMax: "Max Force",
    gearShift: "Gear Shift Thump",
    revLimit: "Rev Limiter",
    advanced: "Advanced",
    reset: "Reset to Defaults",
  },
}[lang];

// Compact icon (24x24 viewBox, simple shape)
const Icon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" />
    <path d="M12 7v4M8 10L5 8M16 10l3-2" />
    <path d="M6 15c1.5-2 3-2.5 6-2.5s4.5 0.5 6 2.5" />
  </svg>
);

const SettingsUI = () => {
  const [s, setS] = R.useState<Record<string, any>>({});
  const [paused, setPaused] = R.useState((window as any)._fhds_paused ?? false);

  R.useEffect(() => {
    call("get_settings").then((r: any) => { if (r) setS(r); });
  }, []);

  const set = (key: string, value: any) => {
    setS((prev: any) => ({ ...prev, [key]: value }));
    call("update_setting", key, value);
  };

  return (
    <div>
      <PanelSection title={T.enable}>
        <PanelSectionRow>
          <ToggleField label={T.enable} checked={!paused}
            onChange={(v: boolean) => { setPaused(!v); (window as any)._fhds_paused = !v; call("pause_writes", !v); }} />
        </PanelSectionRow>
      </PanelSection>

      <PanelSection title={T.brake}>
        <PanelSectionRow>
          <ToggleField label={T.brakeOn} checked={s.brake_enabled ?? true} onChange={(v: boolean) => set("brake_enabled", v)} />
        </PanelSectionRow>
        <PanelSectionRow>
          <SliderField label={T.brakeMax} value={s.brake_max_force ?? 180} min={0} max={255} step={1} onChange={(v: number) => set("brake_max_force", v)} />
        </PanelSectionRow>
        <PanelSectionRow>
          <SliderField label={T.brakeCurve} value={s.brake_curve ?? 2.0} min={0.5} max={5.0} step={0.1} onChange={(v: number) => set("brake_curve", v)} />
        </PanelSectionRow>
        <PanelSectionRow>
          <ToggleField label={T.abs} checked={s.abs_enabled ?? true} onChange={(v: boolean) => set("abs_enabled", v)} />
        </PanelSectionRow>
      </PanelSection>

      <PanelSection title={T.throttle}>
        <PanelSectionRow>
          <ToggleField label={T.throttleOn} checked={s.throttle_enabled ?? true} onChange={(v: boolean) => set("throttle_enabled", v)} />
        </PanelSectionRow>
        <PanelSectionRow>
          <SliderField label={T.throttleMax} value={s.throttle_max_force ?? 130} min={0} max={255} step={1} onChange={(v: number) => set("throttle_max_force", v)} />
        </PanelSectionRow>
        <PanelSectionRow>
          <ToggleField label={T.gearShift} checked={s.gear_shift_enabled ?? true} onChange={(v: boolean) => set("gear_shift_enabled", v)} />
        </PanelSectionRow>
        <PanelSectionRow>
          <ToggleField label={T.revLimit} checked={s.rev_limiter_enabled ?? true} onChange={(v: boolean) => set("rev_limiter_enabled", v)} />
        </PanelSectionRow>
      </PanelSection>

      <PanelSection title={T.advanced}>
        <PanelSectionRow>
          <ButtonItem onClick={() => {
            call("reset_settings").then(() => call("get_settings")).then((r: any) => { if (r) setS(r); });
          }}>{T.reset}</ButtonItem>
        </PanelSectionRow>
      </PanelSection>
    </div>
  );
};

export default definePlugin(() => ({
  title: T.title,
  icon: <Icon />,
  content: <SettingsUI />,
}));
