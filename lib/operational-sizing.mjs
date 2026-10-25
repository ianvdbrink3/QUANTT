/** Research sizing arithmetic. No broker connection or recommended inputs. */
/**
 * @typedef {object} SizingInput
 * @property {number|null} equity
 * @property {number|null} percent
 * @property {number|null} atr
 * @property {number|null} cost
 * @property {number|null} [stopDistance]
 * @property {number|null} [freeMargin]
 * @property {number|null} [marginPerContract]
 */
/** @param {SizingInput} input */
export function calculateSizing({equity,percent,atr,cost,stopDistance=null,freeMargin=null,marginPerContract=null}) {
  const positive=value=>typeof value==='number'&&Number.isFinite(value)&&value>0;
  if(!positive(equity)||!positive(percent)||percent>100||!positive(atr)) return null;
  const budget=equity*percent/100;
  const atrQuantity=Math.floor(budget/(2*atr));
  const confirmedCost=typeof cost==='number'&&Number.isFinite(cost)&&cost>=0;
  const stopQuantity=positive(stopDistance)&&confirmedCost?Math.floor(budget/(2*stopDistance+cost)):null;
  const marginKnown=typeof freeMargin==='number'&&Number.isFinite(freeMargin)&&freeMargin>=0&&positive(marginPerContract);
  const marginCap=marginKnown?Math.floor(freeMargin/marginPerContract):null;
  return {budget,atrQuantity,stopQuantity,marginCap,
    cappedAtr:marginCap===null?null:Math.min(atrQuantity,marginCap),
    cappedStop:marginCap===null||stopQuantity===null?null:Math.min(stopQuantity,marginCap)};
}

/** @param {SizingInput} inputs @param {string} leg */
export function calculateForLeg(inputs,leg){
  /** @type {number|null} */
  let stopDistance=null;
  if(leg==='S1') stopDistance=Math.floor(inputs.atr*.5/.25+1e-9)*.25;
  if(leg==='B'){
    const d=inputs.stopDistance;
    const minimum=Math.ceil(.35*inputs.atr/.25-1e-9)*.25;
    if(typeof d==='number'&&Number.isFinite(d)&&d>=minimum&&Math.abs(d/.25-Math.round(d/.25))<1e-8) stopDistance=d;
  }
  const result=calculateSizing({...inputs,stopDistance});
  return result?{...result,leg,plannedStopDistance:stopDistance}:null;
}
